from django.db import models
from django.conf import settings

from workflow.model_utils import LoggingModel

class MaktabTanfizi(models.Model):
    name = models.CharField(max_length=255, verbose_name="المكتب التنفيذي")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="maktab_tanfizi_user",verbose_name="المستخدم")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "المكتب التنفيذي"
        verbose_name_plural = "المكاتب التنفيذية"

class MaktabTanfiziJiha(models.Model):
    maktab_tanfizi = models.ForeignKey(
        MaktabTanfizi,
        on_delete=models.PROTECT,
        verbose_name="المكتب التنفيذي"
    )

    name = models.CharField(max_length=255, verbose_name="جهة الخطاب")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "جهة الخطاب"
        verbose_name_plural = "جهات الخطاب"

class Khatabat(LoggingModel):  # جدول_خطابات
    maktab_tanfizi = models.ForeignKey(
        MaktabTanfizi,
        on_delete=models.PROTECT,
        verbose_name="المكتب التنفيذي"
    )

    letter_number = models.CharField(
        max_length=100,
        primary_key=True,
        verbose_name="رقم الخطاب"
    )
    subject = models.TextField(verbose_name="موضوع الخطاب")

    def __str__(self):
        return self.letter_number

    class Meta:
        ordering = ["-letter_number"]
        verbose_name = "الخطاب"
        verbose_name_plural = "الخطابات"

class HarkatKhatabat(models.Model):  # جدول_حركة_الخطابات
    MOVEMENT_INBOX = 1
    MOVEMENT_OUTBOX = 2

    MOVEMENT_CHOICES = {
        MOVEMENT_INBOX: "وارد",
        MOVEMENT_OUTBOX: "صادر",
    }

    FOLLOWUP_DONE = 1
    FOLLOWUP_NOT_DONE =  2

    FOLLOWUP_CHOICES = {
        FOLLOWUP_DONE: "تم",
        FOLLOWUP_NOT_DONE: "لم يتم",
    }

    PROCEDURE_1 = 1
    PROCEDURE_2 = 2
    PROCEDURE_3 = 3
    PROCEDURE_4 = 4
    PROCEDURE_5 = 5
    PROCEDURE_6 = 6
    PROCEDURE_7 = 7
    PROCEDURE_8 = 8
    PROCEDURE_9 = 9

    PROCEDURE_CHOICES = {
        PROCEDURE_1: "توصية",
        PROCEDURE_2: "للإجراء",
        PROCEDURE_3: "للتشاور",
        PROCEDURE_4: "للإفادة",
        PROCEDURE_5: "تصدق",
        PROCEDURE_6: "للإطلاع والإحاطة",
        PROCEDURE_7: "للعمل بموجبه",
        PROCEDURE_8: "للإحاطة واجراء اللازم",
        PROCEDURE_9: "للإطلاع وابداء الرأي",
    }

    letter = models.ForeignKey(
        Khatabat,
        on_delete=models.PROTECT,
        verbose_name="رقم الخطاب"
    )
    movement_type = models.IntegerField(verbose_name="نوع الحركة", choices=MOVEMENT_CHOICES)
    date = models.DateField(verbose_name="التاريخ")
    source_entity = models.ForeignKey(MaktabTanfiziJiha, on_delete=models.PROTECT, related_name="source_entities", verbose_name="جهة الخطاب")
    procedure = models.IntegerField(verbose_name="الإجراء", choices=PROCEDURE_CHOICES)
    letter_attachment = models.FileField(upload_to='khatabat/', verbose_name="صورة الخطاب", null=True, blank=True)
    forwarded_to = models.ForeignKey(MaktabTanfiziJiha, on_delete=models.PROTECT, null=True, blank=True, related_name="forwarded_to", verbose_name="الجهة المحول لها")
    forward_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التحويل")
    # receiver_signature = models.BooleanField(default=False, verbose_name="توقيع المستلم")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التسليم")
    followup_result = models.IntegerField(default=FOLLOWUP_NOT_DONE, choices=FOLLOWUP_CHOICES, verbose_name="نتيجة المتابعة",)
    followup_attachment = models.FileField(upload_to='mutabaah/', null=True, blank=True, verbose_name="صورة نتيجة المتابعة")
    note = models.TextField(verbose_name="ملاحظات", null=True, blank=True)

    def __str__(self):
        return f"{self.get_movement_type_display()}/{self.date}/{self.source_entity}"
    
    class Meta:
        verbose_name = "حركة خطاب"
        verbose_name_plural = "حركة الخطابات"
