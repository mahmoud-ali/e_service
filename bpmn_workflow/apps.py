from django.apps import AppConfig


class BpmnWorkflowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bpmn_workflow'
    verbose_name = 'BPMN Workflow Engine'
