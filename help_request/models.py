from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import FileSystemStorage

class HelpRecord(models.Model):
    def attachement_path(self, filename):
        date = self.created_at.date()
        return "help_request/{0}/{1}/{2}".format(self.issue_app,date, filename)    

    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by")) 
    issue_app = models.CharField(_('app name'),max_length=20)
    issue_url = models.URLField(_('page url'),max_length=200)
    issue_txt = models.TextField(_('describe issue'),max_length=200)
    issue_img = models.ImageField(_('capture'),upload_to=attachement_path)
    issue_solved = models.BooleanField(_('issue_solved'),default=False)

    def __str__(self) -> str:
        return _('help request')+': '+f'{self.created_by}/{self.issue_app}'
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _('help request')
        verbose_name_plural = _('help requests')