from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.utils import flatten_fieldsets, unquote
from django.contrib.admin.options import TO_FIELD_VAR
from workflow.admin_utils import view_model_states, get_inline_mixin, create_main_form, get_workflow_mixin

class MockModel:
    state = 1

    def get_next_states(self, user):
        return [(2, "Next State")]

    def can_transition_to_next_state(self, user, next_state):
        return True

    def transition_to_next_state(self, user, next_state):
        self.state = next_state[0]

class MockInline:
    model = MockModel

class MockAdmin(admin.ModelAdmin):
    model = MockModel

class AdminUtilsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.group = Group.objects.create(name='testgroup')
        self.user.groups.add(self.group)
        self.user.save()

    def test_view_model_states(self):
        inline_val = {
            "groups": {
                "testgroup": {
                    "permissions": {
                        1: {"view": True},
                        2: {"view": False},
                    }
                }
            }
        }
        user_groups = ["testgroup"]
        view_states = view_model_states(inline_val, user_groups, ['view'])
        self.assertEqual(view_states, {1})

    def test_get_inline_mixin(self):
        inline_class = {
            "groups": {
                "testgroup": {
                    "permissions": {
                        1: {"change": True},
                        2: {"change": False},
                    }
                }
            }
        }
        InlineMixin = get_inline_mixin(inline_class)
        inline_mixin_instance = InlineMixin()
        request = self.factory.get('/')
        request.user = self.user
        obj = MockModel()
        self.assertTrue(inline_mixin_instance.has_change_permission(request, obj))
        obj.state = 2
        self.assertFalse(inline_mixin_instance.has_change_permission(request, obj))

    def test_create_main_form(self):
        main_class = {
            'model': MockModel,
            'kwargs': {}
        }
        inline_classes = {
            'MockInline': {
                'model': MockModel,
                'kwargs': {},
                'mixins': []
            }
        }
        global_mixins = []
        model_admin, inlines = create_main_form(main_class, inline_classes, global_mixins)
        self.assertTrue(issubclass(model_admin, admin.ModelAdmin))
        self.assertIn('MockInline', inlines)

    def test_get_workflow_mixin(self):
        main_class = {
            'model': MockModel,
            'kwargs': {},
            "groups": {
                "testgroup": {
                    "permissions": {
                        1: {"change": True},
                        2: {"change": False},
                    }
                }
            }
        }
        inline_classes = {
            'MockInline': {
                'model': MockModel,
                'kwargs': {},
                'mixins': [],
                'groups': {}
            }
        }
        inlines_dict = {
            'MockInline': MockInline
        }
        WorkflowAdminLogMixin = get_workflow_mixin(main_class, inline_classes, inlines_dict)
        workflow_admin_instance = WorkflowAdminLogMixin()
        request = self.factory.get('/')
        request.user = self.user
        obj = MockModel()
        self.assertTrue(workflow_admin_instance.has_change_permission(request, obj))
        obj.state = 2
        self.assertFalse(workflow_admin_instance.has_change_permission(request, obj))