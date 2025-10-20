from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    LANG_AR = "ar"
    LANG_EN = "en"

    LANG_CHOICES = {
        LANG_AR: _("Arabic"),
        LANG_AR: _("English"),
    }
            
    lang = models.CharField(max_length=2, choices=LANG_CHOICES, default=LANG_AR)
    usable_password = models.BooleanField(default=True)

    def __str__(self):
        return self.email
        
