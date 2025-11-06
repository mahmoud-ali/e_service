from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import NeedsRequest, SuggestedItem, Department
from .permissions import has_action_permission

class NeedsRequestPermissionsTest(TestCase):

    def setUp(self):
        # Create groups
        self.eom_pub_group = Group.objects.create(name='eom_pub')
        self.dga_pub_group = Group.objects.create(name='dga_pub')
        self.sd_pub_group = Group.objects.create(name='sd_pub')

        # Create users
        self.eom_user = User.objects.create_user(username='eom', password='password')
        self.dga_user = User.objects.create_user(username='dga', password='password')
        self.sd_user = User.objects.create_user(username='sd', password='password')

        # Assign groups to users
        self.eom_user.groups.add(self.eom_pub_group)
        self.dga_user.groups.add(self.dga_pub_group)
        self.sd_user.groups.add(self.sd_pub_group)

        # Create a department and assign the eom_user as executive manager
        self.department = Department.objects.create(name='Test Department', executive_manager=self.eom_user)

        # Create a suggested item
        self.suggested_item = SuggestedItem.objects.create(name='Test Item')

        # Create a needs request
        self.needs_request = NeedsRequest.objects.create(
            date='2025-01-01',
            department=self.department,
            approval_status='draft'
        )

        self.client = Client()

    def test_create_view_eom_user(self):
        self.client.login(username='eom', password='password')
        response = self.client.get(reverse('needs_request_create'))
        self.assertEqual(response.status_code, 200)

    def test_create_view_dga_user_forbidden(self):
        self.client.login(username='dga', password='password')
        response = self.client.get(reverse('needs_request_create'))
        self.assertEqual(response.status_code, 403)

    def test_update_view_eom_user_draft(self):
        self.client.login(username='eom', password='password')
        response = self.client.get(reverse('needs_request_update', args=[self.needs_request.pk]))
        self.assertEqual(response.status_code, 200)

    def test_update_view_dga_user_draft(self):
        self.client.login(username='dga', password='password')
        response = self.client.get(reverse('needs_request_update', args=[self.needs_request.pk]))
        self.assertEqual(response.status_code, 200)

    def test_update_view_sd_user_draft_forbidden(self):
        self.client.login(username='sd', password='password')
        response = self.client.get(reverse('needs_request_update', args=[self.needs_request.pk]))
        self.assertEqual(response.status_code, 403)

    def test_detail_view_eom_user_draft(self):
        self.client.login(username='eom', password='password')
        response = self.client.get(reverse('needs_request_detail', args=[self.needs_request.pk]))
        self.assertEqual(response.status_code, 200)

    def test_detail_view_sd_user_draft_forbidden(self):
        self.client.login(username='sd', password='password')
        response = self.client.get(reverse('needs_request_detail', args=[self.needs_request.pk]))
        self.assertEqual(response.status_code, 403)

    def test_has_action_permission_function(self):
        self.assertTrue(has_action_permission(self.dga_user, self.needs_request, 'dga_approval'))

    def test_dga_approval_action_dga_user(self):
        self.client.login(username='dga', password='password')
        response = self.client.post(reverse('needs_request_detail', args=[self.needs_request.pk]), {'action': 'dga_approval'})
        self.assertEqual(response.status_code, 302) # Redirects on success
        self.needs_request.refresh_from_db()
        self.assertEqual(self.needs_request.approval_status, 'dga_approval')

    def test_dga_approval_action_eom_user_forbidden(self):
        self.client.login(username='eom', password='password')
        response = self.client.post(reverse('needs_request_detail', args=[self.needs_request.pk]), {'action': 'dga_approval'})
        self.assertEqual(response.status_code, 403)