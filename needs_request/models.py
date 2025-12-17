from django.db import models
from django.conf import settings

from django.contrib.contenttypes.models import ContentType

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    executive_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='executive_manager_of')
    department_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='department_manager_of')

    def __str__(self):
        return self.name

class SuggestedItem(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_it_related = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class NeedsRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('dga_approval', 'موافقة مدير الإدارة العامة'),
        ('dga_rejection', 'رفض مدير الإدارة العامة'),
        ('sd_comment', 'تعليق قسم الإمداد'),
        ('doa_comment', 'تعليق مدير الشؤون الإدارية'),
        ('it_comment', 'تعليق مدير تقنية المعلومات'),
        ('dgdhra_recommendation', 'توصية مدير الإدارة العامة للموارد البشرية والإدارية'),
        ('dgfa_recommendation', 'توصية مدير الإدارة العامة للشؤون المالية'),
        ('agmfa_approval', 'موافقة مساعد المدير العام للشؤون المالية والإدارية'),
        ('agmfa_rejection', 'رفض مساعد المدير العام للشؤون المالية والإدارية'),
        ('gm_approval', 'موافقة المدير العام'),
        ('gm_rejection', 'رفض المدير العام'),
    ]

    date = models.DateField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    cause = models.TextField()
    others = models.TextField(blank=True, null=True)
    sd_comment = models.TextField(blank=True, null=True)
    doa_comment = models.TextField(blank=True, null=True)
    it_comment = models.TextField(blank=True, null=True)
    dgdhra_recommendation = models.TextField(blank=True, null=True)
    dgfa_recommendation = models.TextField(blank=True, null=True)
    approval_status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    rejection_cause = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Needs Request from {self.department} on {self.date}"
    
    def is_final_status(self):
        workflow = self.get_workflow()
        status = None
        if workflow:
            status = workflow.status

        if status in ('terminated','completed',):
            return True
        
        return False
    
    def is_approved(self):
        workflow = self.get_workflow()
        status = None
        if workflow:
            status = workflow.status

        if status in ('completed',):
            return True
        
        return False
    
    def is_rejected(self):
        workflow = self.get_workflow()
        status = None
        if workflow:
            status = workflow.status

        if status in ('terminated',):
            return True
        
        return False
    
    # BPMN Workflow Integration
    def get_workflow(self):
        """Get the active workflow process instance for this request"""
        from bpmn_workflow.models import ProcessInstance
        content_type = ContentType.objects.get_for_model(self)
        return ProcessInstance.objects.filter(
            content_type=content_type,
            object_id=self.pk
        ).first()
    
    def get_workflow_status(self):
        """Get current workflow status (active, completed, etc.)"""
        workflow = self.get_workflow()
        return workflow.status if workflow else 'draft'
    
    def get_current_tasks(self):
        """Get all active tasks for this request"""
        workflow = self.get_workflow()
        if workflow:
            return workflow.get_current_tasks()
        return []
    
    def get_workflow_timeline(self):
        """Get complete audit trail of workflow actions"""
        from bpmn_workflow.engine import BPMNEngine
        workflow = self.get_workflow()
        if workflow:
            return BPMNEngine.get_timeline(workflow)
        return []
    
    def can_user_act(self, user):
        """Check if user can act on any current task"""
        for task in self.get_current_tasks():
            if task.can_be_completed_by(user):
                return True
        return False

class Item(models.Model):
    needs_request = models.ForeignKey(NeedsRequest, on_delete=models.PROTECT, related_name='items')
    requested_item = models.ForeignKey(SuggestedItem, on_delete=models.PROTECT)
    no_of_requested_items = models.IntegerField(default=0)
    no_of_approved_items = models.IntegerField(default=0)

    def __str__(self):
        return self.requested_item.name