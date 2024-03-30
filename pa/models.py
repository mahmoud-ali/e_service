import datetime

from django.db import models
from django.conf import settings
from django.forms import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.contrib.auth import get_user_model

from company_profile.models import TblCompanyProduction

CURRENCY_TYPE_SDG = "sdg"
CURRENCY_TYPE_EURO = "euro"

CURRENCY_TYPE_CHOICES = {
    CURRENCY_TYPE_SDG: _("sdg"),
    CURRENCY_TYPE_EURO: _("euro"),
}

STATE_TYPE_DRAFT = 'draft'
STATE_TYPE_CONFIRM = 'confirm'

STATE_TYPE_CHOICES = {
    STATE_TYPE_DRAFT: _("draft"),
    STATE_TYPE_CONFIRM: _("confirm"),
}

def validate_positive(value):
    if value <= 0:
        raise ValidationError(_("value should be positive"))

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
        
class LkpItem(models.Model):
    name = models.CharField(_("item_name"),max_length=50)

    def __str__(self):
        return _("Financial item") +" "+str(self.name)
        
class TblCompanyCommitment(LoggingModel):
    INTERVAL_TYPE_MANUAL = 'manual'
    INTERVAL_TYPE_YEAR = 'year'

    INTERVAL_TYPE_CHOICES = {
        INTERVAL_TYPE_MANUAL: _('manual'),
        INTERVAL_TYPE_YEAR: _('yearly'),
    }

    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    item  = models.ForeignKey(LkpItem, on_delete=models.PROTECT,verbose_name=_("financial item"))    
    amount = models.FloatField(_("amount"))
    currency = models.CharField(_("currency"),max_length=10, choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_EURO)
    state = models.CharField(_("record_state"),max_length=10, choices=STATE_TYPE_CHOICES, default=STATE_TYPE_DRAFT)

    request_interval = models.CharField(_("interval"),max_length=10, choices=INTERVAL_TYPE_CHOICES, default=INTERVAL_TYPE_MANUAL)
    request_next_interval_dt = models.DateField(_("next_interval_dt"),null=True,blank=True)
    request_auto_confirm = models.BooleanField(_("request_auto_confirm"),default=False)
    
    def __str__(self):
        return self.company.__str__()+"/"+self.item.name
        
    def get_absolute_url(self): 
        return reverse('pa:commitment_show',args=[str(self.id)])                

    def clean(self):
        if self.request_interval != self.INTERVAL_TYPE_MANUAL and not self.request_next_interval_dt:
            raise ValidationError(
                {"request_next_interval_dt":_("field is required")}
            )
        
    def generate_request(self):
        if self.state == STATE_TYPE_DRAFT:
            return
        
        if self.request_interval != self.INTERVAL_TYPE_MANUAL and self.request_next_interval_dt <= timezone.now().date():
            to_date = self.request_next_interval_dt
            if self.request_interval == self.INTERVAL_TYPE_YEAR:
                to_date += datetime.timedelta(days=364)

            state_val = STATE_TYPE_DRAFT
            if self.request_auto_confirm:
                state_val = STATE_TYPE_CONFIRM

            admin_user = get_user_model().objects.get(id=1)

            request = TblCompanyRequest.objects.create(
                commitement=self,
                from_dt=self.request_next_interval_dt,
                to_dt = to_date,
                amount = self.amount,
                currency = self.currency,
                state = state_val,
                created_by = admin_user,
                updated_by = admin_user
            )

            request.send_email()

            self.request_next_interval_dt = to_date + datetime.timedelta(days=1)
            self.save()

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Financial commitment")
        verbose_name_plural = _("Financial commitments")
        constraints = [
            models.UniqueConstraint(fields=['company', 'item'], name='unique_commitment')
        ]

        indexes = [
            models.Index(fields=["company", "item"]),
            models.Index(fields=["company"]),
            models.Index(fields=["item"]),
        ]

class TblCompanyRequest(LoggingModel):
    REQUEST_PAYMENT_NO_PAYMENT = "no"
    REQUEST_PAYMENT_PARTIAL_PAYMENT = "partial"
    REQUEST_PAYMENT_FULL_PAYMENT = "full"

    REQUEST_PAYMENT_CHOICES = {
        REQUEST_PAYMENT_NO_PAYMENT: _("no_payment"),
        REQUEST_PAYMENT_PARTIAL_PAYMENT: _("partial_payment"),
        REQUEST_PAYMENT_FULL_PAYMENT: _("full_payment"),
    }

    commitement  = models.ForeignKey(TblCompanyCommitment, on_delete=models.PROTECT,verbose_name=_("commitement"))    
    from_dt = models.DateField(_("from_dt"))
    to_dt = models.DateField(_("to_dt"))
    amount = models.FloatField(_("amount"),validators=[validate_positive])
    currency = models.CharField(_("currency"),max_length=10, choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_EURO)
    payment_state = models.CharField(_("payment_state"),max_length=10, choices=REQUEST_PAYMENT_CHOICES, default=REQUEST_PAYMENT_NO_PAYMENT)
    state = models.CharField(_("record_state"),max_length=10, choices=STATE_TYPE_CHOICES, default=STATE_TYPE_DRAFT)
    
    def __str__(self):
        return self.commitement.__str__()+" ("+str(self.amount)+" "+CURRENCY_TYPE_CHOICES[self.currency]+")" #+" ("+str(self.from_dt)+" - "+str(self.to_dt)+") "
        
    def get_absolute_url(self): 
        return reverse('pa:request_show',args=[str(self.id)])                

    def clean(self):        
        qs = TblCompanyRequest.objects.filter(
            commitement__company__id=self.commitement.company.id,
            commitement__item__id=self.commitement.item.id,
        )
        if self.id:
            qs = qs.exclude(id=self.id)

        if self.to_dt < self.from_dt:
            raise ValidationError(
                {"to_dt":_("to_dt should be great or equal than from_dt")}
            )
        
        if qs.filter(from_dt__lte=self.from_dt, to_dt__gte=self.from_dt).count() > 0:
            raise ValidationError(
                {"from_dt":_("conflicted date")}
            )
        
        if qs.filter(from_dt__lte=self.to_dt, to_dt__gte=self.to_dt).count() > 0:
            raise ValidationError(
                {"to_dt":_("conflicted date")}
            )
        
        if qs.filter(from_dt__gte=self.from_dt, to_dt__lte=self.to_dt).count() > 0:
            raise ValidationError(
                {
                    "from_dt":_("conflicted date"),
                    "to_dt":_("conflicted date"),
                }
            )

    def sum_of_payment(self,exclude=0,confirmed_only=False):
        if self.state == STATE_TYPE_DRAFT:
            return 0
        
        sum = 0
        qs = self.tblcompanypayment_set
        if exclude:
            qs = qs.exclude(id=exclude)
        else:
            qs = qs.all()

        if confirmed_only:
            qs = qs.filter(state=STATE_TYPE_CONFIRM)

        for p in qs:
            if p.currency == self.currency:
                sum += p.amount
            else:
                sum += p.amount*p.excange_rate

        return sum

    def update_payment_state(self):
        if self.state == STATE_TYPE_DRAFT:
            return
        sum = self.sum_of_payment(confirmed_only=True)
        if sum == self.amount:
            self.payment_state =  self.REQUEST_PAYMENT_FULL_PAYMENT
        elif sum < self.amount:
            self.payment_state =  self.REQUEST_PAYMENT_PARTIAL_PAYMENT

        self.save()

    def send_email(self):
        if self.state == STATE_TYPE_DRAFT:
            return
        
        print("Not implemented yet!")

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Financial request")
        verbose_name_plural = _("Financial requests")
        indexes = [
            models.Index(fields=["commitement"]),
        ]

class TblCompanyPayment(LoggingModel):
    request  = models.ForeignKey(TblCompanyRequest, on_delete=models.PROTECT,verbose_name=_("request"))    
    payment_dt = models.DateField(_("payment_dt"))
    amount = models.FloatField(_("amount"),validators=[validate_positive])
    currency = models.CharField(_("currency"),max_length=10, choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_EURO)
    excange_rate = models.FloatField(_("excange_rate"),validators=[validate_positive],default=1)
    state = models.CharField(_("record_state"),max_length=10, choices=STATE_TYPE_CHOICES, default=STATE_TYPE_DRAFT)
    
    def __str__(self):
        return _("Financial payment") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('pa:payment_show',args=[str(self.id)])                

    def clean(self):
        sum = self.request.sum_of_payment(exclude=self.id)
        if self.currency == self.request.currency:
            sum += self.amount
        else:
            sum += self.amount*self.excange_rate

        if sum > self.request.amount:
            raise ValidationError(
                {"amount":_("sum of payments more than request amount: ")+str(self.request.amount)+ " "+CURRENCY_TYPE_CHOICES[self.request.currency]}
            )

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Financial payment")
        verbose_name_plural = _("Financial payments")
        indexes = [
            models.Index(fields=["request"]),
        ]
