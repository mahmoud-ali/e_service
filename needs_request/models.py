from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    executive_manager = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='executive_manager_of')
    department_manager = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='department_manager_of')

    def __str__(self):
        return self.name

class SuggestedItem(models.Model):
    name = models.CharField(max_length=255, unique=True)

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
        if self.approval_status in ('dga_rejection', 'agmfa_rejection', 'gm_approval', 'gm_rejection'):
            return True
        
        return False
    
    def is_approved(self):
        if self.approval_status in ('gm_approval',):
            return True
        
        return False
    
    def is_rejected(self):
        if self.approval_status in ('dga_rejection', 'agmfa_rejection', 'gm_rejection'):
            return True
        
        return False

class Item(models.Model):
    needs_request = models.ForeignKey(NeedsRequest, on_delete=models.PROTECT, related_name='items')
    requested_item = models.ForeignKey(SuggestedItem, on_delete=models.PROTECT)

    def __str__(self):
        return self.requested_item.name