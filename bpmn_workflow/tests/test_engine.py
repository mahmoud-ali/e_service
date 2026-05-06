from unittest.mock import patch, MagicMock
import importlib
from bpmn_workflow.models import WorkflowDefinition, BPMNNode, SequenceFlow, Token, ActivityLog
from bpmn_workflow.engine import BPMNEngine, get_workflow_handler, BaseWorkflowHandler
from .base import BPMNTestBase, TestHandler

class BPMNEngineVerificationTest(BPMNTestBase):
    def test_start_process(self):
        """Test starting a process and initial token creation at UserTask"""
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        self.assertEqual(process.status, 'active')
        # Should have an active token at UserTask_1
        active_tokens = process.tokens.filter(is_active=True)
        self.assertTrue(active_tokens.exists())
        self.assertEqual(active_tokens.first().current_node, self.user_node)
        
    def test_secure_eval_condition(self):
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user, initial_variables={'amount': 100})
        self.assertTrue(BPMNEngine._evaluate_condition("variables['amount'] > 50", process))
        self.assertFalse(BPMNEngine._evaluate_condition("variables['amount'] < 50", process))
        self.assertFalse(BPMNEngine._evaluate_condition("__import__('os').system('ls')", process))

    @patch('bpmn_workflow.engine.get_workflow_handler')
    def test_service_task_error_handling(self, mock_get_handler):
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        # Move token to service task
        service_token = Token.objects.create(process_instance=process, current_node=self.service_node, status='active', is_active=True)
        
        mock_get_handler.return_value = TestHandler()
        
        BPMNEngine._handle_service_task(service_token, self.user)
        
        service_token.refresh_from_db()
        log = ActivityLog.objects.filter(process_instance=process, event_type='task_failed').first()
        
        self.assertEqual(service_token.status, 'error')
        self.assertIsNotNone(log)
        if log:
            self.assertIn("Custom Service Error", log.details.get('error'))

    def test_variable_persistence(self):
        """Test that data from user task completion is persisted to process variables"""
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        task = process.tasks.filter(status='ready').first()
        
        test_data = {'approved': True, 'amount_confirmed': 500}
        BPMNEngine.complete_task(task, self.user, test_data)
        
        process.refresh_from_db()
        self.assertEqual(process.variables.get('approved'), True)
        self.assertEqual(process.variables.get('amount_confirmed'), 500)

    def test_parallel_gateway(self):
        """Test parallel split and join logic"""
        # Create a dedicated workflow for this test
        wf = WorkflowDefinition.objects.create(key='parallel_wf', name='Parallel WF', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start_p', node_type='start_event', name='Start')
        split_node = BPMNNode.objects.create(workflow=wf, bpmn_id='split', name='Parallel Split', node_type='parallel_gateway')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f0', source=start, target=split_node)
        task1_node = BPMNNode.objects.create(workflow=wf, bpmn_id='task1', name='Task 1', node_type='user_task')
        task2_node = BPMNNode.objects.create(workflow=wf, bpmn_id='task2', name='Task 2', node_type='user_task')
        join_node = BPMNNode.objects.create(workflow=wf, bpmn_id='join', name='Parallel Join', node_type='parallel_gateway')
        end_node = BPMNNode.objects.create(workflow=wf, bpmn_id='end_parallel', name='End Parallel', node_type='end_event')

        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=split_node, target=task1_node)
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f2', source=split_node, target=task2_node)
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f3', source=task1_node, target=join_node)
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f4', source=task2_node, target=join_node)
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f5', source=join_node, target=end_node)

        process = BPMNEngine.start_process('parallel_wf', self.content_object, self.user, initial_variables={'approved': True})
        active_tokens = process.tokens.filter(is_active=True)
        self.assertEqual(active_tokens.count(), 2)
        node_ids = set(active_tokens.values_list('current_node__bpmn_id', flat=True))
        self.assertEqual(node_ids, {'task1', 'task2'})

        # 2. Complete task 1 -> reach join
        ti1 = process.tasks.get(node=task1_node, status='ready')
        BPMNEngine.complete_task(ti1, self.user, {})
        
        join_token = process.tokens.filter(current_node=join_node, is_active=True).first()
        self.assertIsNotNone(join_token)
        self.assertEqual(join_token.status, 'active')
        
        process.refresh_from_db()
        self.assertEqual(process.status, 'active')

        # 3. Complete task 2 -> reach join and trigger it
        ti2 = process.tasks.get(node=task2_node, status='ready')
        BPMNEngine.complete_task(ti2, self.user, {})
        
        final_token = process.tokens.filter(current_node=end_node).first()
        self.assertIsNotNone(final_token)
        process.refresh_from_db()
        self.assertEqual(process.status, 'completed')
        
    def test_exclusive_gateway_complex(self):
        """Test Exclusive Gateway with multiple conditions and default path"""
        wf = WorkflowDefinition.objects.create(key='exclusive_wf', name='Exclusive WF', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start_e', node_type='start_event', name='Start')
        gateway = BPMNNode.objects.create(workflow=wf, bpmn_id='exclusive', name='Choice', node_type='exclusive_gateway')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='fe0', source=start, target=gateway)
        path_a = BPMNNode.objects.create(workflow=wf, bpmn_id='path_a', name='Path A', node_type='service_task')
        path_b = BPMNNode.objects.create(workflow=wf, bpmn_id='path_b', name='Path B', node_type='service_task')
        default_path = BPMNNode.objects.create(workflow=wf, bpmn_id='path_def', name='Default Path', node_type='service_task')
        
        f_a = SequenceFlow.objects.create(workflow=wf, bpmn_id='flow_a', source=gateway, target=path_a, condition_expression="score > 90")
        f_b = SequenceFlow.objects.create(workflow=wf, bpmn_id='flow_b', source=gateway, target=path_b, condition_expression="score <= 90 and score > 50")
        f_def = SequenceFlow.objects.create(workflow=wf, bpmn_id='flow_def', source=gateway, target=default_path)
        
        gateway.default_flow = 'flow_def'
        gateway.save()

        # Score 95 -> Path A
        process_a = BPMNEngine.start_process('exclusive_wf', self.content_object, self.user)
        process_a.variables['score'] = 95
        process_a.save()
        
        token_a = process_a.tokens.filter(current_node=gateway).first()
        self.assertIsNotNone(token_a)
        BPMNEngine._handle_exclusive_gateway(token_a, self.user)
        self.assertTrue(process_a.tokens.filter(current_node=path_a).exists())

        # Score 70 -> Path B
        process_b = BPMNEngine.start_process('exclusive_wf', self.content_object, self.user)
        process_b.variables['score'] = 70
        process_b.save()
        token_b = process_b.tokens.filter(current_node=gateway).first()
        self.assertIsNotNone(token_b)
        BPMNEngine._handle_exclusive_gateway(token_b, self.user)
        self.assertTrue(process_b.tokens.filter(current_node=path_b).exists())

        # Score 30 -> Default Path
        process_c = BPMNEngine.start_process('exclusive_wf', self.content_object, self.user)
        process_c.variables['score'] = 30
        process_c.save()
        token_c = process_c.tokens.filter(current_node=gateway).first()
        self.assertIsNotNone(token_c)
        BPMNEngine._handle_exclusive_gateway(token_c, self.user)
        self.assertTrue(process_c.tokens.filter(current_node=default_path).exists())

    def test_engine_service_task_failure(self):
        """Test service task handler failure"""
        wf = WorkflowDefinition.objects.create(key='fail_wf', name='Fail WF', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start_f', node_type='start_event')
        task = BPMNNode.objects.create(workflow=wf, bpmn_id='service_f', node_type='service_task', name='Service F')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='flow_f1', source=start, target=task)
        
        # Create a handler that fails
        class FailingHandler:
            def handle_service_f(self, process, user):
                raise ValueError("Intentional Failure")
            def set_variable(self, process, key, value): pass
            def get_variable(self, process, key): return None
        
        with patch('bpmn_workflow.engine.get_workflow_handler', return_value=FailingHandler()):
            # Use a fresh transaction/process to avoid poisoning
            process = BPMNEngine.start_process('fail_wf', self.content_object, self.user)
            token = process.tokens.filter(current_node=task).first()
            self.assertEqual(token.status, 'error')
            self.assertTrue(ActivityLog.objects.filter(process_instance=process, event_type='task_failed').exists())
            
            # Test re-execution after fixing (simulated by retrying with _move_token)
            with patch('bpmn_workflow.engine.get_workflow_handler', return_value=MagicMock()):
                token.status = 'active'
                token.save()
                BPMNEngine._move_token(token, self.user)
                token.refresh_from_db()
                self.assertEqual(token.status, 'completed')

    def test_engine_gateway_failure(self):
        """Test gateway condition evaluation failure"""
        wf = WorkflowDefinition.objects.create(key='gate_fail_wf', name='Gate Fail WF', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start_g', node_type='start_event')
        gate = BPMNNode.objects.create(workflow=wf, bpmn_id='gate_g', node_type='exclusive_gateway')
        end = BPMNNode.objects.create(workflow=wf, bpmn_id='end_g', node_type='end_event')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='flow_g1', source=start, target=gate)
        # Invalid condition pointing to end
        SequenceFlow.objects.create(workflow=wf, bpmn_id='flow_g2', source=gate, target=end, condition_expression="1/0")
        
        process = BPMNEngine.start_process('gate_fail_wf', self.content_object, self.user)
        token = process.tokens.filter(current_node=end).first()
        self.assertIsNotNone(token)

    def test_engine_get_variable(self):
        """Test BaseWorkflowHandler.get_variable"""
        from bpmn_workflow.engine import BaseWorkflowHandler
        handler = BaseWorkflowHandler()
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        self.assertEqual(handler.get_variable(process, 'nonexistent', default='foo'), 'foo')
        handler.set_variable(process, 'exists', 'bar')
        self.assertEqual(handler.get_variable(process, 'exists'), 'bar')

    def test_engine_dynamic_service_task(self):
        """Test service task with dotted implementation path"""
        wf = WorkflowDefinition.objects.create(key='dynamic_wf', name='Dynamic WF', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        service = BPMNNode.objects.create(
            workflow=wf, 
            bpmn_id='service', 
            node_type='service_task',
            implementation='bpmn_workflow.tests.base.dummy_function'
        )
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=service)
        
        process = BPMNEngine.start_process('dynamic_wf', self.content_object, self.user)
        token = process.tokens.filter(current_node=service).first()
        self.assertEqual(token.status, 'completed')
        self.assertEqual(process.variables.get('dummy'), 'value')

    def test_engine_get_timeline(self):
        """Test BPMNEngine.get_timeline"""
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        timeline = BPMNEngine.get_timeline(process)
        self.assertGreater(len(timeline), 0)
        self.assertEqual(timeline[0].event_type, 'process_started')

    def test_get_workflow_handler_config_fail(self):
        """Test get_workflow_handler with failing config"""
        from bpmn_workflow.engine import BaseWorkflowHandler
        wf = WorkflowDefinition.objects.create(key='fail_wf', handler_class='non.existent.Class')
        handler = get_workflow_handler(wf)
        self.assertIsInstance(handler, BaseWorkflowHandler)
    def test_get_workflow_handler_success(self):
        """Test get_workflow_handler with a valid handler_class (Covers lines 49-50) using standard lib"""
        import logging
        wf = WorkflowDefinition.objects.create(
            key='success_wf', 
            handler_class='logging.Handler'
        )
        handler = get_workflow_handler(wf)
        self.assertIsInstance(handler, logging.Handler)

    def test_engine_no_flow_gateway(self):
        """Test gateway with no outgoing flows (covers lines 408-410)"""
        wf = WorkflowDefinition.objects.create(key='no_out_flow_wf', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        gate = BPMNNode.objects.create(workflow=wf, bpmn_id='gate', node_type='exclusive_gateway')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=gate)
        
        process = BPMNEngine.start_process('no_out_flow_wf', self.content_object, self.user)
        token = process.tokens.filter(current_node=gate).first()
        self.assertEqual(token.status, 'error')

    def test_get_workflow_handler_generated(self):
        """Test get_workflow_handler with generated module"""
        from bpmn_workflow.engine import BaseWorkflowHandler
        wf = WorkflowDefinition.objects.create(key='gen_wf')
        with patch('importlib.util.find_spec') as mock_find_spec:
            mock_find_spec.return_value = MagicMock()
            with patch('importlib.util.module_from_spec') as mock_mod_from_spec:
                mock_module = MagicMock()
                mock_mod_from_spec.return_value = mock_module
                mock_module.GenWfHandler = type('GenWfHandler', (BaseWorkflowHandler,), {})
                handler = get_workflow_handler(wf)
                self.assertEqual(handler.__class__.__name__, 'GenWfHandler')

    def test_start_process_no_start_event(self):
        """Test start_process fails if no start event exists"""
        wf = WorkflowDefinition.objects.create(key='no_start_wf', is_active=True)
        with self.assertRaises(ValueError):
            BPMNEngine.start_process('no_start_wf', self.content_object, self.user)

    def test_complete_task_handler_exception(self):
        """Test complete_task when handler method raises exception"""
        wf = WorkflowDefinition.objects.create(key='fail_user_wf', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        task_node = BPMNNode.objects.create(workflow=wf, bpmn_id='fail_task', node_type='user_task')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=task_node)
        
        process = BPMNEngine.start_process('fail_user_wf', self.content_object, self.user)
        task = process.tasks.first()
        
        with patch('bpmn_workflow.engine.get_workflow_handler') as mock_get:
            mock_get.return_value = TestHandler()
            with self.assertRaises(Exception):
                BPMNEngine.complete_task(task, self.user, {})
            
        task.refresh_from_db()
        self.assertEqual(task.status, 'ready')

    def test_complete_task_with_dict_output(self):
        """Test complete_task when handler returns a dict (covers lines 164-167)"""
        wf = WorkflowDefinition.objects.create(key='dict_user_wf', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        task_node = BPMNNode.objects.create(workflow=wf, bpmn_id='UserTask_1', node_type='user_task')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=task_node)
        
        process = BPMNEngine.start_process('dict_user_wf', self.content_object, self.user)
        task = process.tasks.first()
        
        with patch('bpmn_workflow.engine.get_workflow_handler') as mock_get:
            mock_get.return_value = TestHandler()
            BPMNEngine.complete_task(task, self.user, {'original': 'data'})
            
        process.refresh_from_db()
        self.assertEqual(process.variables.get('processed'), True)
        self.assertEqual(process.variables.get('score'), 100)
        self.assertEqual(process.variables.get('original'), 'data')

    def test_move_token_unhandled_type(self):
        """Test logger warning for unhandled node type"""
        wf = WorkflowDefinition.objects.create(key='unhandled_wf', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        mystery = BPMNNode.objects.create(workflow=wf, bpmn_id='mystery', node_type='mystery_node')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=mystery)
        
        with self.assertLogs('bpmn_workflow.engine', level='WARNING') as cm:
            BPMNEngine.start_process('unhandled_wf', self.content_object, self.user)
            self.assertTrue(any("Unhandled node type: mystery_node" in output for output in cm.output))

    def test_handle_start_event_no_flows(self):
        """Test start event with no outgoing flows"""
        wf = WorkflowDefinition.objects.create(key='no_flow_start_wf', is_active=True)
        BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        
        with self.assertLogs('bpmn_workflow.engine', level='WARNING') as cm:
            process = BPMNEngine.start_process('no_flow_start_wf', self.content_object, self.user)
            self.assertTrue(any("has no outgoing flows" in output for output in cm.output))
        
        token = process.tokens.first()
        self.assertFalse(token.is_active)

    def test_service_task_dynamic_import_fail(self):
        """Test failure in dynamic service task import"""
        wf = WorkflowDefinition.objects.create(key='dynamic_fail_wf', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        service = BPMNNode.objects.create(
            workflow=wf, 
            bpmn_id='service', 
            node_type='service_task',
            implementation='non.existent.module.func'
        )
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=service)
        
        process = BPMNEngine.start_process('dynamic_fail_wf', self.content_object, self.user)
        token = process.tokens.filter(current_node=service).first()
        self.assertEqual(token.status, 'error')

    def test_service_task_output_extra_keys(self):
        """Test service task output with extra keys stored as variables"""
        wf = WorkflowDefinition.objects.create(key='extra_keys_wf', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        service = BPMNNode.objects.create(
            workflow=wf, 
            bpmn_id='service', 
            node_type='service_task',
            implementation='bpmn_workflow.tests.base.dummy_extra_keys'
        )
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=service)
        
        # Need to define dummy_extra_keys in tests.base or somewhere accessible
        with patch('bpmn_workflow.tests.base.dummy_extra_keys') as mock_dummy:
            mock_dummy.return_value = {'status': 'success', 'extra_calc': 123}
            # Actually the code uses implementation string to import. 
            # I'll use the existing dummy_extra_keys in tests.base
            service.implementation = 'bpmn_workflow.tests.base.dummy_extra_keys'
            service.save()
            process = BPMNEngine.start_process('extra_keys_wf', self.content_object, self.user)
            self.assertEqual(process.variables.get('extra_calc'), 123)

    def test_service_task_waiting(self):
        """Test service task returning status='waiting'"""
        wf = WorkflowDefinition.objects.create(key='waiting_wf', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        service = BPMNNode.objects.create(
            workflow=wf, 
            bpmn_id='service', 
            node_type='service_task',
            implementation='bpmn_workflow.tests.base.dummy_waiting'
        )
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=service)
        
        process = BPMNEngine.start_process('waiting_wf', self.content_object, self.user)
        token = process.tokens.filter(current_node=service).first()
        self.assertEqual(token.status, 'waiting')

    def test_exclusive_gateway_custom_evaluator(self):
        """Test exclusive gateway with custom evaluator on handler"""
        wf = WorkflowDefinition.objects.create(key='custom_gate_wf', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        gate = BPMNNode.objects.create(workflow=wf, bpmn_id='gate', node_type='exclusive_gateway')
        end = BPMNNode.objects.create(workflow=wf, bpmn_id='end', node_type='end_event')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=gate)
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f_target', source=gate, target=end)
        
        with patch('bpmn_workflow.engine.get_workflow_handler') as mock_get:
            mock_get.return_value = TestHandler()
            process = BPMNEngine.start_process('custom_gate_wf', self.content_object, self.user)
            self.assertTrue(process.tokens.filter(current_node=end).exists())

    def test_exclusive_gateway_exception(self):
        """Test exclusive gateway exception handling"""
        wf = WorkflowDefinition.objects.create(key='gate_exc_wf', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        gate = BPMNNode.objects.create(workflow=wf, bpmn_id='gate_crash', node_type='exclusive_gateway')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=gate)
        
        with patch('bpmn_workflow.engine.get_workflow_handler') as mock_get:
            mock_get.return_value = TestHandler()
            process = BPMNEngine.start_process('gate_exc_wf', self.content_object, self.user)
            token = process.tokens.filter(current_node=gate).first()
            self.assertEqual(token.status, 'error')

    def test_parallel_gateway_pass_through(self):
        """Test parallel gateway with 1 incoming/1 outgoing flow"""
        wf = WorkflowDefinition.objects.create(key='parallel_pass_wf', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        gate = BPMNNode.objects.create(workflow=wf, bpmn_id='gate', node_type='parallel_gateway')
        end = BPMNNode.objects.create(workflow=wf, bpmn_id='end', node_type='end_event')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=gate)
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f2', source=gate, target=end)
        
        process = BPMNEngine.start_process('parallel_pass_wf', self.content_object, self.user)
        self.assertTrue(process.tokens.filter(current_node=end).exists())

    def test_handle_end_event_custom(self):
        """Test end event with custom pre_end_event handler"""
        wf = WorkflowDefinition.objects.create(key='end_handler_wf', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        end = BPMNNode.objects.create(workflow=wf, bpmn_id='end', node_type='end_event')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=end)
        
        with patch('bpmn_workflow.engine.get_workflow_handler') as mock_get:
            mock_get.return_value = TestHandler()
            process = BPMNEngine.start_process('end_handler_wf', self.content_object, self.user)
            self.assertTrue(process.variables.get('end_ran'))

    def test_parallel_gateway_join_wait(self):
        """Test parallel join waiting for all tokens"""
        wf = WorkflowDefinition.objects.create(key='parallel_join_wf', is_active=True)
        start = BPMNNode.objects.create(workflow=wf, bpmn_id='start', node_type='start_event')
        split = BPMNNode.objects.create(workflow=wf, bpmn_id='split', node_type='parallel_gateway')
        t1 = BPMNNode.objects.create(workflow=wf, bpmn_id='t1', node_type='user_task')
        t2 = BPMNNode.objects.create(workflow=wf, bpmn_id='t2', node_type='user_task')
        join = BPMNNode.objects.create(workflow=wf, bpmn_id='join', node_type='parallel_gateway')
        end = BPMNNode.objects.create(workflow=wf, bpmn_id='end', node_type='end_event')
        
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f1', source=start, target=split)
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f2', source=split, target=t1)
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f3', source=split, target=t2)
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f4', source=t1, target=join)
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f5', source=t2, target=join)
        SequenceFlow.objects.create(workflow=wf, bpmn_id='f6', source=join, target=end)
        
        process = BPMNEngine.start_process('parallel_join_wf', self.content_object, self.user)
        task1 = process.tasks.get(node__bpmn_id='t1')
        
        # Complete only one task
        BPMNEngine.complete_task(task1, self.user, {})
        
        # Join should NOT have happened yet
        self.assertFalse(process.tokens.filter(current_node=end).exists())
        self.assertTrue(process.tokens.filter(current_node=join, is_active=True).exists())
        
        # Complete second task
        task2 = process.tasks.get(node__bpmn_id='t2')
        BPMNEngine.complete_task(task2, self.user, {})
        
        # Now join should have occurred
        self.assertTrue(process.tokens.filter(current_node=end).exists())
