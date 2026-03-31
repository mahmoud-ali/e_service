from unittest.mock import patch
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from bpmn_workflow.models import WorkflowDefinition, BPMNNode, Token
from bpmn_workflow.engine import BPMNEngine
from .base import BPMNTestBase

User = get_user_model()

class CoreAPIVerificationTest(BPMNTestBase):
    def test_api_import_workflow(self):
        data = {
            'key': 'new_workflow',
            'xml': self.bpmn_xml,
            'name': 'API Imported Workflow'
        }
        url = reverse('workflow-import-workflow')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(WorkflowDefinition.objects.filter(key='new_workflow').exists())

    def test_api_execute_retry(self):
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        token = Token.objects.create(process_instance=process, current_node=self.service_node, status='error', is_active=True)
        
        url = reverse('process-instance-execute', kwargs={'pk': process.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Retried 1 tokens', response.data['status'])

    def test_api_history(self):
        """Test the process instance history API"""
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        url = reverse('process-instance-history', kwargs={'pk': process.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['event_type'], 'process_started')

    def test_api_unauthorized(self):
        """Test that API actions require authentication"""
        self.client.logout()
        url = reverse('workflow-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_api_invalid_task_completion(self):
        """Test completing a task in an invalid state"""
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        task = process.tasks.filter(status='ready').first()
        BPMNEngine.complete_task(task, self.user, {})
        
        url = reverse('task-complete', kwargs={'pk': task.id})
        response = self.client.post(url, data={'data': {}}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_api_start_failures(self):
        """Test failures of starting a process via API"""
        url = reverse('workflow-start', kwargs={'key': 'test_workflow'})
        # Missing parameters
        response = self.client.post(url, data={}, format='json')
        self.assertEqual(response.status_code, 400)
        # Invalid content type
        response = self.client.post(url, data={'content_type': 9999, 'object_id': 1}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_api_execute_no_tokens(self):
        """Test execute API when no error tokens exist"""
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        url = reverse('process-instance-execute', kwargs={'pk': process.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('No error tokens found', response.data['status'])

    def test_api_task_complete_permissions(self):
        """Test non-superuser trying to complete task not assigned to them"""
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        task = process.tasks.filter(status='ready').first()
        other_user = User.objects.create_user(username='other', password='password')
        self.client.force_authenticate(user=other_user)
        
        url = reverse('task-complete', kwargs={'pk': task.id})
        response = self.client.post(url, data={'data': {}}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_api_complete_invalid_data(self):
        """Test API complete with invalid data types"""
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        task = process.tasks.get(status='ready')
        url = reverse('task-complete', kwargs={'pk': task.id})
        self.client.force_authenticate(user=self.user)
        
        with patch('bpmn_workflow.engine.BPMNEngine.complete_task', side_effect=ValueError("Validation Error")):
            response = self.client.post(url, data={'data': {}}, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data['error'], "Validation Error")

        with patch('bpmn_workflow.engine.BPMNEngine.complete_task', side_effect=Exception("General Error")):
            response = self.client.post(url, data={'data': {}}, format='json')
            self.assertEqual(response.status_code, 500)
            self.assertIn("General Error", response.data['error'])

    def test_api_import_workflow_validation(self):
        url = reverse('workflow-import-workflow')
        response = self.client.post(url, data={}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_api_import_workflow_error(self):
        url = reverse('workflow-import-workflow')
        with patch('bpmn_workflow.importer.WorkflowSyncService.sync') as mock_sync:
            mock_sync.side_effect = Exception("Sync failed")
            response = self.client.post(url, data={'key': 'new_wf', 'xml': 'some xml'}, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data['error'], "Sync failed")

    def test_api_start_success(self):
        ct = ContentType.objects.get_for_model(User)
        url = reverse('workflow-start', kwargs={'key': 'test_workflow'})
        data = {
            'content_type': ct.pk,
            'object_id': self.user.pk,
            'variables': {'init': 'val'}
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['status'], 'active')

    def test_api_execute_retry_failure(self):
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        token = process.tokens.filter(is_active=True).first()
        token.status = 'error'
        token.save()
        
        url = reverse('process-instance-execute', kwargs={'pk': process.id})
        with patch('bpmn_workflow.engine.BPMNEngine._move_token') as mock_move:
            mock_move.side_effect = Exception("Move failed")
            response = self.client.post(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['status'], 'Retried 0 tokens')

    def test_api_active_tasks(self):
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        task = process.tasks.first()
        task.assignee = self.user
        task.save()
        
        url = reverse('task-active')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(task.id))

    def test_api_complete_success(self):
        process = BPMNEngine.start_process('test_workflow', self.content_object, self.user)
        task = process.tasks.first()
        task.assignee = self.user
        task.save()
        
        url = reverse('task-complete', kwargs={'pk': task.id})
        response = self.client.post(url, data={'data': {}}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'Task completed successfully')
