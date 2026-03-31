from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework.test import APIClient
from bpmn_workflow.models import WorkflowDefinition, BPMNNode, Token, TaskInstance
from bpmn_workflow.engine import BPMNEngine

User = get_user_model()

class ShamilPortalAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='shamil_user', password='password', email='shamil@example.com')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.workflow = WorkflowDefinition.objects.create(
            key='shamil_wf',
            name='Shamil Workflow',
            bpmn_xml="<bpmn:definitions xmlns:bpmn=\"http://www.omg.org/spec/BPMN/20100524/MODEL\"><bpmn:process id=\"p1\" /></bpmn:definitions>",
            is_active=True,
            version=1
        )
        BPMNNode.objects.create(workflow=self.workflow, bpmn_id='start', node_type='start_event', name='Start')
        
        self.process = BPMNEngine.start_process('shamil_wf', self.user, self.user)
        self.task = TaskInstance.objects.create(
            process_instance=self.process,
            node=BPMNNode.objects.create(workflow=self.workflow, bpmn_id='task_1', node_type='user_task', name='Task 1'),
            token=Token.objects.create(process_instance=self.process, current_node=self.workflow.nodes.get(bpmn_id='start')),
            status='ready',
            assignee=self.user
        )

    def test_dashboard_summary(self):
        url = reverse('dashboard-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['active_requests_count'], 1)
        self.assertEqual(response.data['waiting_tasks_count'], 1)

    def test_portal_home_view(self):
        url = reverse('portal-home')
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Shamil Employee Portal', response.content.decode())

    def test_my_requests_list_and_filter(self):
        url = reverse('my-requests-list')
        # Active filter
        response = self.client.get(url, {'status': 'active'})
        self.assertEqual(response.status_code, 200)
        
        # Branch 172 coverage: Mock the response data to look like a paginated one 
        # (or just test that the code handles both if we can trigger actual pagination)
        # Since we just want coverage, we can also ensure we hit it.
        results = response.data['results'] if isinstance(response.data, dict) and 'results' in response.data else response.data
        self.assertTrue(len(results) >= 1)
        self.assertIn('progress_percentage', results[0])

        # Force line 172 by patching if needed, but the code ALREADY has the check.
        # Let's just make sure we actually hit line 172. 
        # If the view has pagination, it will hit it. If not, it won't.
        # I'll check if pagination is enabled.

        # Archive filter
        response = self.client.get(url, {'status': 'archived'})
        self.assertEqual(response.status_code, 200)
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 0)

    def test_start_new_request(self):
        url = reverse('my-requests-list')
        data = {
            'workflow_key': 'shamil_wf',
            'content_type': ContentType.objects.get_for_model(User).id,
            'object_id': self.user.id,
            'variables': {'test': True}
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['variables']['test'], True)

    def test_task_inbox_urgent_and_claim(self):
        url = reverse('task-inbox-list')
        # Urgent filter
        self.task.due_date = timezone.now() + timezone.timedelta(hours=2)
        self.task.save()
        response = self.client.get(url, {'urgent': 'true'})
        self.assertEqual(response.status_code, 200)
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 1)

        # Claim task
        claim_url = reverse('task-inbox-claim', kwargs={'pk': self.task.id})
        response = self.client.post(claim_url)
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'in_progress')

    def test_task_inbox_complete(self):
        complete_url = reverse('task-inbox-complete', kwargs={'pk': self.task.id})
        response = self.client.post(complete_url, data={'data': {'approved': True}}, format='json')
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')

    def test_process_timeline(self):
        url = reverse('process-timeline', kwargs={'pk': self.process.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)

    def test_comments_list_and_create(self):
        url = reverse('comment-list')
        # Create comment
        response = self.client.post(url, data={
            'process_instance': self.process.id,
            'text': 'Test comment'
        }, format='json')
        self.assertEqual(response.status_code, 201)
        
        # List comments
        response = self.client.get(url, {'process_instance': self.process.id})
        self.assertEqual(response.status_code, 200)
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['text'], 'Test comment')

    def test_unauthorized_shamil_access(self):
        self.client.logout()
        url = reverse('dashboard-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_workflow_mixin_exceptions(self):
        from unittest.mock import patch
        from bpmn_workflow.portal_api import WorkflowMixin
        mixin = WorkflowMixin()
        
        with patch('bpmn_workflow.engine.BPMNEngine.complete_task', side_effect=PermissionError("Perm error")):
            success, msg = mixin.perform_task_transition(self.task, self.user, {})
            self.assertFalse(success)
            self.assertEqual(msg, "Perm error")
            
        with patch('bpmn_workflow.engine.BPMNEngine.complete_task', side_effect=ValueError("Val error")):
            success, msg = mixin.perform_task_transition(self.task, self.user, {})
            self.assertFalse(success)
            self.assertEqual(msg, "Val error")

        with patch('bpmn_workflow.engine.BPMNEngine.complete_task', side_effect=Exception("Gen error")):
            success, msg = mixin.perform_task_transition(self.task, self.user, {})
            self.assertFalse(success)
            self.assertIn("An unexpected error occurred", msg)

    def test_start_new_request_failures(self):
        url = reverse('my-requests-list')
        
        # Missing fields
        response = self.client.post(url, data={}, format='json')
        self.assertEqual(response.status_code, 400)
        
        # Workflow not found
        data = {
            'workflow_key': 'nonexistent',
            'content_type': ContentType.objects.get_for_model(User).id,
            'object_id': self.user.id
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 404)
        
        # Invalid ContentType
        data = {
            'workflow_key': 'shamil_wf',
            'content_type': 9999,
            'object_id': 1
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_task_claim_invalid_status(self):
        self.task.status = 'in_progress'
        self.task.save()
        url = reverse('task-inbox-claim', kwargs={'pk': self.task.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn("already claimed or completed", response.data['error'])

    def test_task_complete_failure(self):
        url = reverse('task-inbox-complete', kwargs={'pk': self.task.id})
        from unittest.mock import patch
        with patch('bpmn_workflow.portal_api.WorkflowMixin.perform_task_transition', return_value=(False, "Transition Failed")):
            response = self.client.post(url, data={'data': {}}, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data['error'], "Transition Failed")

    def test_process_timeline_security(self):
        other_user = User.objects.create_user(username='other_portal', password='password')
        self.client.force_authenticate(user=other_user)
        url = reverse('process-timeline', kwargs={'pk': self.process.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_comment_list_no_process(self):
        url = reverse('comment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 0)

    def test_comment_security(self):
        other_user = User.objects.create_user(username='other_commenter', password='password')
        self.client.force_authenticate(user=other_user)
        url = reverse('comment-list')
        response = self.client.get(url, {'process_instance': self.process.id})
        self.assertEqual(response.status_code, 200)
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 0)

    def test_my_requests_list_paginated(self):
        """Specifically test the paginated response branch in portal_api.py (Line 172)"""
        url = reverse('my-requests-list')
        from unittest.mock import patch
        from rest_framework.response import Response
        
        # Mocking the list method of the base mixin used by the viewset
        mock_data = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [{'id': str(self.process.id), 'status': 'active'}]
        }
        
        # Patch ListModelMixin.list since ReadOnlyModelViewSet inherits from it
        with patch('rest_framework.mixins.ListModelMixin.list', return_value=Response(mock_data)):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            # Ensure we hit line 172
            self.assertIn('results', response.data)
            self.assertIn('progress_percentage', response.data['results'][0])
