from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from company_profile.models import LkpState

class LoggingModel(models.Model):
    """
    An abstract base class model that provides self-
    updating ``created_at`` and ``updated_at`` fields for responsable user.
    """
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
    class Meta:
        abstract = True

# class LkpStateDetails(models.Model):
#     state = models.OneToOneField(LkpState, on_delete=models.PROTECT,related_name="state_representative",verbose_name=_("state"))
#     code = models.CharField(_("code"),max_length=4)
#     next_serial_no = models.IntegerField(_("export_next_serial_no"))
    
#     class Meta:
#         verbose_name = _("dabtiaat state detail")
#         verbose_name_plural = _("dabtiaat state details")

class TblStateRepresentative2(models.Model):
    AUTHORITY_SMRC = 2
    AUTHORITY_APPROVED = 3
    # AUTHORITY_SHORTAT_2LM3ADIN = 4
    # AUTHORITY_2LESTIKHBARAT_2L3ASKRIA = 5
    # AUTHORITY_SMRC_NAFIZA = 6

    AUTHORITY_CHOICES = {
        AUTHORITY_SMRC: _('authority_smrc'),
        # AUTHORITY_APPROVED: _('authority_approved'),
        # AUTHORITY_SHORTAT_2LM3ADIN: _('authority_shortat_2lm3adin'),
        # AUTHORITY_2LESTIKHBARAT_2L3ASKRIA: _('authority_2lestikhbarat_2l3askria'),
        # AUTHORITY_SMRC_NAFIZA: _('authority_smrc_nafiza'),
    }

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="state_representative2",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    authority = models.IntegerField(_("authority"), choices=AUTHORITY_CHOICES, default=AUTHORITY_SMRC)

    def __str__(self):
        return f'{self.user} ({self.state.name})'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['state', 'authority'], name='unique_state_authority_dabtiaat')
        ]

        verbose_name = _("state representative")
        verbose_name_plural = _("state representatives")

from django.utils import timezone

class AppDabtiaat(LoggingModel):

    STATE_DRAFT = 1
    STATE_SMRC = 2
    STATE_APPROVED = 3
    # STATE_SHORTAT_2LM3ADIN = 4
    # STATE_2LESTIKHBARAT_2L3ASKRIA = 5
    # STATE_SSMO = 6
    # STATE_WAIVED = 7
    STATE_CANCELED = 8

    STATE_CHOICES = {
        STATE_DRAFT: _('state_draft'),
        STATE_SMRC: _('state_smrc'),
        STATE_APPROVED: _('state_approved'),
        # STATE_SHORTAT_2LM3ADIN: _('state_shortat_2lm3adin'),
        # STATE_2LESTIKHBARAT_2L3ASKRIA: _('state_2lestikhbarat_2l3askria'),
        # STATE_SSMO: _('state_ssmo'),
        # STATE_WAIVED: _('state_waived'),
        STATE_CANCELED: _('state_canceled'),
    }

    def attachement_path(self, filename):
        date = self.created_at.date()
        return "dabtiaat/{0}/{1}".format(date, filename)    

    date = models.DateField(_("date"))
    report_number = models.CharField(_("Report number"), max_length=20, null=True, blank=True,default='')
    # gold_weight_in_gram = models.FloatField(_("gold_weight_in_gram"))
    # gold_price = models.FloatField(_("gold_price"))
    # gold_caliber = models.FloatField(_("gold_caliber"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)
    attachement_file = models.FileField(_("attachement_file"),upload_to=attachement_path,null=True,blank=True)
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))

    @property
    def sum_of_weight_in_gram(self):
        total =self.appdabtiaatdetails_set.aggregate(sum=models.Sum("gold_weight_in_gram"))['sum'] or 0

        return total

    @property
    def avg_of_price(self):
        total =self.appdabtiaatdetails_set.aggregate(avg=models.Avg("gold_price"))['avg'] or 0

        return total

    @property
    def sum_of_weight_multiply_price(self):
        qs = self.appdabtiaatdetails_set.all()
        total = 0
        for obj in qs:
            total += obj.gold_weight_in_gram*obj.gold_price
        return total

    @property
    def total_price(self):
        return self.sum_of_weight_multiply_price

    def get_stored_or_live_amount(self, key):
        if self.pk:
            hist = self.calculation_histories.filter(setting_key=key).order_by('-id').first()
            if hist is not None:
                return hist.calculated_amount

        setting = DabtiaatSetting.objects.filter(key=key).first()
        if setting:
            return self.calculate_setting_amount(setting)

        if key == 'total_koli_pct':
            return self.koli_amount_live
        elif key == 'al3wayid_aljalila':
            return self.sum_of_weight_multiply_price * 0.10
        elif key == 'alhafiz':
            return self.sum_of_weight_multiply_price * 0.10
        elif key == 'alniyaba':
            return self.sum_of_weight_multiply_price * 0.02
        elif key in ['smrc', 'state', 'police', 'amn', 'riasat_alquat_aldaabita']:
            return self.alhafiz_amount * 0.10
        elif key == 'alquat_aldaabita':
            return self.alhafiz_amount * 0.50
        return 0.0

    @property
    def al3wayid_aljalila_amount(self):
        return self.get_stored_or_live_amount('al3wayid_aljalila')

    @property
    def alhafiz_amount(self):
        return self.get_stored_or_live_amount('alhafiz')

    @property
    def alniyaba_amount(self):
        return self.get_stored_or_live_amount('alniyaba')

    @property
    def koli_amount_live(self):
        koli_setting = DabtiaatSetting.objects.filter(key='total_koli_pct').first()
        if koli_setting:
            if koli_setting.is_active:
                total_pct = koli_setting.percentage
            else:
                total_pct = 0.0
        else:
            base_total_qs = DabtiaatSetting.objects.filter(calculation_base=DabtiaatSetting.BASE_TOTAL).exclude(key='total_koli_pct')
            if base_total_qs.exists():
                total_pct = sum(s.percentage for s in base_total_qs if s.is_active)
            else:
                total_pct = 22.0
        return self.sum_of_weight_multiply_price * (total_pct / 100.0)

    @property
    def koli_amount(self):
        return self.get_stored_or_live_amount('total_koli_pct')

    @property
    def smrc_amount(self):
        return self.get_stored_or_live_amount('smrc')

    @property
    def state_amount(self):
        return self.get_stored_or_live_amount('state')

    @property
    def police_amount(self):
        return self.get_stored_or_live_amount('police')

    @property
    def amn_amount(self):
        return self.get_stored_or_live_amount('amn')

    @property
    def riasat_alquat_aldaabita_amount(self):
        return self.get_stored_or_live_amount('riasat_alquat_aldaabita')

    @property
    def alquat_aldaabita_amount(self):
        return self.get_stored_or_live_amount('alquat_aldaabita')

    def calculate_setting_amount(self, setting):
        if isinstance(setting, str):
            setting_obj = DabtiaatSetting.objects.filter(key=setting).first()
            if setting_obj:
                return setting_obj.calculate_amount(self)
            return 0.0
        return setting.calculate_amount(self)

    def snapshot_calculations(self, force_date=None):
        if not self.pk:
            return

        calc_date = force_date or timezone.now()
        weight = self.sum_of_weight_in_gram
        total_val = self.sum_of_weight_multiply_price

        self.calculation_histories.all().delete()

        koli_setting = DabtiaatSetting.objects.filter(key='total_koli_pct').first()
        if koli_setting:
            koli_pct = koli_setting.percentage if koli_setting.is_active else 0.0
            is_active_koli = koli_setting.is_active
        else:
            base_total_qs = DabtiaatSetting.objects.filter(calculation_base=DabtiaatSetting.BASE_TOTAL).exclude(key='total_koli_pct')
            if base_total_qs.exists():
                koli_pct = sum(s.percentage for s in base_total_qs if s.is_active)
            else:
                koli_pct = 22.0
            is_active_koli = True

        koli_amt = total_val * (koli_pct / 100.0)
        AppDabtiaatCalculationHistory.objects.create(
            app_dabtiaat=self,
            calculation_date=calc_date,
            total_gold_weight=weight,
            total_gold_value=total_val,
            setting_key='total_koli_pct',
            setting_name=_('إجمالي الكلي'),
            percentage=koli_pct,
            calculation_base=DabtiaatSetting.BASE_TOTAL,
            calculated_amount=koli_amt,
            is_active=is_active_koli
        )

        settings_qs = DabtiaatSetting.objects.exclude(key='total_koli_pct').order_by('id')
        if settings_qs.exists():
            for setting in settings_qs:
                amt = setting.calculate_amount(self)
                AppDabtiaatCalculationHistory.objects.create(
                    app_dabtiaat=self,
                    calculation_date=calc_date,
                    total_gold_weight=weight,
                    total_gold_value=total_val,
                    setting_key=setting.key,
                    setting_name=setting.name,
                    percentage=setting.percentage,
                    calculation_base=setting.calculation_base,
                    calculated_amount=amt,
                    is_active=setting.is_active
                )

    def __getattr__(self, name):
        if name.endswith("_amount") and not name.startswith("_"):
            key = name[:-7]
            if self.pk and self.calculation_histories.filter(setting_key=key).exists():
                return self.get_stored_or_live_amount(key)
            setting = DabtiaatSetting.objects.filter(key=key).first()
            if setting:
                return self.calculate_setting_amount(setting)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __str__(self):
        return f'{self.source_state} ({self.sum_of_weight_in_gram} جرام)'

    class Meta:
        ordering = ["-date","-id"]
        verbose_name = _("dabtiaat app")
        verbose_name_plural = _("dabtiaat app")


class AppDabtiaatCalculationHistory(models.Model):
    app_dabtiaat = models.ForeignKey(AppDabtiaat, on_delete=models.CASCADE, related_name="calculation_histories", verbose_name=_("dabtiaat app"))
    calculation_date = models.DateTimeField(_("تاريخ ووقت الحساب"), default=timezone.now)
    total_gold_weight = models.FloatField(_("إجمالي وزن الذهب (جرام)"), default=0.0)
    total_gold_value = models.FloatField(_("إجمالي قيمة الذهب"), default=0.0)

    setting_key = models.CharField(_("مفتاح البند"), max_length=50, blank=True, null=True)
    setting_name = models.CharField(_("اسم البند"), max_length=100)
    percentage = models.FloatField(_("النسبة (%)"), default=0.0)
    calculation_base = models.CharField(_("أساس الاحتساب"), max_length=20, default='TOTAL')
    calculated_amount = models.FloatField(_("المبلغ المحسوب"), default=0.0)
    is_active = models.BooleanField(_("مفعل وقت الحساب"), default=True)

    class Meta:
        verbose_name = _("سجل حساب الضبطية")
        verbose_name_plural = _("سجلات حسابات الضبطيات")
        ordering = ["-calculation_date", "id"]

    def __str__(self):
        return f"{self.setting_name}: {self.calculated_amount:.2f} ({self.percentage}%)"



class DabtiaatSetting(models.Model):
    BASE_TOTAL = 'TOTAL'
    BASE_HAFIZ = 'HAFIZ'

    BASE_CHOICES = [
        (BASE_TOTAL, _('إجمالي قيمة المضبوطات')),
        (BASE_HAFIZ, _('مبلغ الحافز')),
    ]

    name = models.CharField(_("اسم البند"), max_length=100)
    key = models.CharField(_("مفتاح البند"), max_length=50, blank=True, null=True, unique=True, help_text=_("رمز للتعرف على البند بالنظام (اختياري)"))
    percentage = models.FloatField(_("النسبة (%)"), default=0.0)
    calculation_base = models.CharField(_("أساس الاحتساب"), max_length=20, choices=BASE_CHOICES, default=BASE_TOTAL)
    created_at = models.DateTimeField(_("تاريخ الإضافة"), auto_now_add=True)
    is_active = models.BooleanField(_("مفعل"), default=True)

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"

    def calculate_amount(self, app_dabtiaat):
        if not self.is_active:
            return 0.0
        if self.calculation_base == self.BASE_HAFIZ:
            return app_dabtiaat.alhafiz_amount * (self.percentage / 100.0)
        else:
            return app_dabtiaat.sum_of_weight_multiply_price * (self.percentage / 100.0)

    def clean(self):
        super().clean()
        if self.percentage < 0:
            raise ValidationError(_("رسالة تجاوز: النسبة لا يمكن أن تكون أقل من 0%."))
        if self.percentage > 100:
            raise ValidationError(_("رسالة تجاوز: النسبة لا يمكن أن تتجاوز 100% من المبلغ الكلي."))

        if self.calculation_base == self.BASE_HAFIZ:
            hafiz_sub_qs = DabtiaatSetting.objects.filter(calculation_base=self.BASE_HAFIZ).exclude(pk=self.pk)
            total_hafiz_sub_pct = sum(s.percentage for s in hafiz_sub_qs if s.is_active)
            if self.is_active:
                total_hafiz_sub_pct += self.percentage
            if total_hafiz_sub_pct > 100.0:
                raise ValidationError(_(f"رسالة تجاوز: إجمالي نسب البنود المقتطعة من الحافز ({total_hafiz_sub_pct:.1f}%) يتجاوز 100% من قيمة الحافز!"))

        hafiz_setting = DabtiaatSetting.objects.filter(key='alhafiz').exclude(pk=self.pk).first()
        if self.key == 'alhafiz':
            hafiz_pct = self.percentage if self.is_active else 0.0
        else:
            hafiz_pct = hafiz_setting.percentage if (hafiz_setting and hafiz_setting.is_active) else 10.0

        qs = DabtiaatSetting.objects.exclude(key='total_koli_pct').exclude(pk=self.pk)
        total_effective_pct = 0.0

        if self.is_active:
            if self.calculation_base == self.BASE_HAFIZ:
                total_effective_pct += self.percentage * (hafiz_pct / 100.0)
            else:
                total_effective_pct += self.percentage

        for setting in qs:
            if not setting.is_active:
                continue
            if setting.calculation_base == self.BASE_HAFIZ:
                total_effective_pct += setting.percentage * (hafiz_pct / 100.0)
            else:
                total_effective_pct += setting.percentage

        if total_effective_pct > 100.0:
            raise ValidationError(_(f"رسالة تجاوز: إجمالي النسبة المقتطعة للبنود المفعّلة ({total_effective_pct:.1f}%) يتجاوز 100% من المبلغ الكلي!"))

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.key:
            import re
            slug = re.sub(r'\W+', '_', self.name).strip('_')
            if not slug:
                slug = "band"
            base_key = f"band_{slug}"
            key = base_key
            count = 1
            while DabtiaatSetting.objects.filter(key=key).exclude(pk=self.pk).exists():
                key = f"{base_key}_{count}"
                count += 1
            self.key = key
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("إعداد النسبة والبنود")
        verbose_name_plural = _("إعدادات البنود والنسب")
        ordering = ["id"]

    @classmethod
    def get_percentage(cls, key, default=0.0):
        setting = cls.objects.filter(key=key).first()
        if setting:
            return setting.percentage if setting.is_active else 0.0
        return default

    @classmethod
    def is_active_setting(cls, key):
        setting = cls.objects.filter(key=key).first()
        if setting:
            return setting.is_active
        return True


class AppDabtiaatDetails(models.Model):
    app_dabtiaat = models.ForeignKey(AppDabtiaat, on_delete=models.PROTECT,verbose_name =_("app_dabtiaat"))

    alloy_id = models.CharField(_("alloy_id"),max_length=20,null=True,blank=True, default='')
    gold_weight_in_gram = models.FloatField(_("gold_weight_in_gram"))
    gold_price = models.FloatField(_("gold_price"))
    gold_caliber = models.FloatField(_("gold_caliber"),null=True,blank=True,default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.app_dabtiaat_id and self.app_dabtiaat:
            self.app_dabtiaat.snapshot_calculations()

    class Meta:
        verbose_name = _("تفاصيل استمارة ضبطية")
        verbose_name_plural = _("تفاصيل استمارة ضبطية")

class SettlementType(models.Model):
    name = models.CharField(_("name"),max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("settlement type")
        verbose_name_plural = _("settlement types")

class RevenueSettlement(LoggingModel):
    STATE_DRAFT = 1
    STATE_SMRC = 2
    STATE_APPROVED = 3
    STATE_CANCELED = 8

    STATE_CHOICES = {
        STATE_DRAFT: _('state_draft'),
        STATE_SMRC: _('state_smrc'),
        STATE_APPROVED: _('state_approved'),
        STATE_CANCELED: _('state_canceled'),
    }

    settlement_type = models.ForeignKey(SettlementType, on_delete=models.PROTECT,verbose_name=_("settlement_type"))
    date = models.DateField(_("date"))
    amount = models.FloatField(_("amount"))
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

    def __str__(self):
        return f"{self.settlement_type.name} ({self.date})"

    class Meta:
        ordering = ["-date",]
        verbose_name = _("Revenue Settlement")
        verbose_name_plural = _("Revenue Settlement")
