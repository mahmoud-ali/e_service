import datetime

from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.forms import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from company_profile.models import TblCompany,TblCompanyProduction, TblCompanyProductionLicense, TblCompanyProductionUserRole

CURRENCY_TYPE_SDG = "sdg"
CURRENCY_TYPE_EURO = "euro"
CURRENCY_TYPE_DOLLAR = "dollar"

CURRENCY_TYPE_CHOICES = {
    CURRENCY_TYPE_SDG: _("sdg"),
    CURRENCY_TYPE_EURO: _("euro"),
    CURRENCY_TYPE_DOLLAR: _("dollar"),
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
    CALCULATION_METHOD_FIXED_VALUE = 'fixed_value'
    CALCULATION_METHOD_AREA_KM = 'area_km'
    CALCULATION_METHOD_NO_CONTRACTS = 'no_contracts'

    CALCULATION_METHOD_CHOICES = {
        CALCULATION_METHOD_FIXED_VALUE: _('fixed_value'),
        CALCULATION_METHOD_AREA_KM: _('area_km'),
        CALCULATION_METHOD_NO_CONTRACTS: _('no_contracts'),
    }

    name = models.CharField(_("item_name"),max_length=50)
    company_type = models.CharField(_("company_type"),max_length=15, choices=TblCompany.COMPANY_TYPE_CHOICES)
    calculation_method = models.CharField(_("calculation_method"),max_length=20, choices=CALCULATION_METHOD_CHOICES, default=CALCULATION_METHOD_FIXED_VALUE)

    class Meta:
        ordering = ["id"]
        verbose_name = _("Financial item")
        verbose_name_plural = _("Financial items")

    def __str__(self):
        return _("Financial item") +" "+str(self.name)
    
    def calculate_value(self,factor,company):
        if self.calculation_method == self.CALCULATION_METHOD_FIXED_VALUE:
            return factor
        elif self.calculation_method == self.CALCULATION_METHOD_AREA_KM:
            total_area = TblCompanyProductionLicense.objects \
                            .filter(company=company,contract_status=1) \
                            .aggregate(total=Sum('area'))['total']
            return factor*total_area
        elif self.calculation_method == self.CALCULATION_METHOD_NO_CONTRACTS:
            total_contracts = TblCompanyProductionLicense.objects \
                            .filter(company=company,contract_status=1) \
                            .count()
            return factor*total_contracts
        
class TblCompanyOpenningBalanceMaster(LoggingModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    currency = models.CharField(_("currency"),max_length=10, choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_EURO)
    state = models.CharField(_("record_state"),max_length=10, choices=STATE_TYPE_CHOICES, default=STATE_TYPE_DRAFT)
    
    def __str__(self):
        return self.company.__str__()+"/"+self.currency
        
    def get_absolute_url(self): 
        return reverse('pa:openning_balance_show',args=[str(self.id)])                

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Openning balance")
        verbose_name_plural = _("Openning balances")
        indexes = [
            models.Index(fields=["company"]),
        ]

class TblCompanyOpenningBalanceDetail(models.Model):
    commitment_master  = models.ForeignKey(TblCompanyOpenningBalanceMaster, on_delete=models.PROTECT)
    item  = models.ForeignKey(LkpItem, on_delete=models.PROTECT,verbose_name=_("financial item"))    
    amount = models.FloatField(_("amount"))

    class Meta:
        ordering = ["id"]
        verbose_name = _("Openning balance detail")
        verbose_name_plural = _("Openning balance details")

    def clean(self):
        if self.commitment_master.company.company_type != self.item.company_type:
            raise ValidationError(
                {"item":_("item type should match company type")}
            )


class TblCompanyCommitmentMaster(LoggingModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    license  = models.ForeignKey(TblCompanyProductionLicense, on_delete=models.PROTECT,verbose_name=_("license"),null=True,blank=True)    
    currency = models.CharField(_("currency"),max_length=10, choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_EURO)
    state = models.CharField(_("record_state"),max_length=10, choices=STATE_TYPE_CHOICES, default=STATE_TYPE_DRAFT)
    
    def __str__(self):
        return self.company.__str__()+"/"+self.currency
        
    def get_absolute_url(self): 
        return reverse('pa:commitment_show',args=[str(self.id)])                

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Financial commitment")
        verbose_name_plural = _("Financial commitments")
        indexes = [
            models.Index(fields=["company"]),
        ]

    def clean(self):
        if self.company != self.license.company:
            raise ValidationError(
                {"license":_("choose license belong to company")}
            )
        if not self.license and self.company.company_type in (TblCompany.COMPANY_TYPE_EMTIAZ,TblCompany.COMPANY_TYPE_ENTAJ,TblCompany.COMPANY_TYPE_MOKHALFAT):
            raise ValidationError(
                {"license":""}
            )

class TblCompanyCommitmentDetail(models.Model):
    commitment_master  = models.ForeignKey(TblCompanyCommitmentMaster, on_delete=models.PROTECT)
    item  = models.ForeignKey(LkpItem, on_delete=models.PROTECT,verbose_name=_("financial item"))    
    amount_factor = models.FloatField(_("amount_factor"))

    class Meta:
        ordering = ["id"]
        verbose_name = _("Financial commitment detail")
        verbose_name_plural = _("Financial commitment details")

    def clean(self):
        if hasattr(self.commitment_master,'company') and hasattr(self,"item"):
            if self.commitment_master.company.company_type != self.item.company_type:
                raise ValidationError(
                    {"item":_("item type should match company type")}
                )

class TblCompanyCommitmentSchedular(LoggingModel):
    INTERVAL_TYPE_MANUAL = 'manual'
    INTERVAL_TYPE_YEAR = 'year'

    INTERVAL_TYPE_CHOICES = {
        INTERVAL_TYPE_MANUAL: _('manual'),
        INTERVAL_TYPE_YEAR: _('yearly'),
    }

    commitment = models.OneToOneField(TblCompanyCommitmentMaster, on_delete=models.PROTECT,related_name="commitment_schedular",verbose_name=_("commitment"))
    request_interval = models.CharField(_("interval"),max_length=10, choices=INTERVAL_TYPE_CHOICES, default=INTERVAL_TYPE_MANUAL)
    request_next_interval_dt = models.DateField(_("next_interval_dt"),null=True,blank=True)
    request_auto_confirm = models.BooleanField(_("request_auto_confirm"),default=False)
    state = models.CharField(_("record_state"),max_length=10, choices=STATE_TYPE_CHOICES, default=STATE_TYPE_DRAFT)

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Financial commitment schedular")
        verbose_name_plural = _("Financial commitment schedulars")

    def get_to_date(self):
        to_date = self.request_next_interval_dt
        if self.request_interval == self.INTERVAL_TYPE_YEAR:
            to_date += datetime.timedelta(days=364)

        return to_date
    
    def clean(self):
        if self.request_interval != self.INTERVAL_TYPE_MANUAL and not self.request_next_interval_dt:
            raise ValidationError(
                {"request_next_interval_dt":_("field is required")}
            )

        qs = TblCompanyRequestMaster.objects.filter(
            commitment__company__id=self.commitment.company.id,
        )
        if self.id:
            qs = qs.exclude(id=self.id)

        from_date = self.request_next_interval_dt
        to_date = self.get_to_date()

        if to_date < from_date:
            raise ValidationError(
                {"to_dt":_("to_dt should be great or equal than from_dt")}
            )
        
        if qs.filter(from_dt__lte=from_date, to_dt__gte=from_date).count() > 0 or \
            qs.filter(from_dt__lte=to_date, to_dt__gte=to_date).count() > 0 or \
            qs.filter(from_dt__gte=from_date, to_dt__lte=to_date).count() > 0:
            raise ValidationError(
                {"request_next_interval_dt":_("conflicted date")}
            )
        

    def generate_request(self):
        if self.state == STATE_TYPE_DRAFT or self.commitment.state == STATE_TYPE_DRAFT:
            return

        if self.request_interval != self.INTERVAL_TYPE_MANUAL and self.request_next_interval_dt <= timezone.now().date():
            to_date = self.get_to_date()

            state_val = STATE_TYPE_DRAFT
            if self.request_auto_confirm:
                state_val = STATE_TYPE_CONFIRM

            admin_user = get_user_model().objects.get(id=1)

            request_master = TblCompanyRequestMaster.objects.create(
                commitment=self.commitment,
                from_dt=self.request_next_interval_dt,
                to_dt = to_date,
                currency = self.commitment.currency,
                state = state_val,
                created_by = admin_user,
                updated_by = admin_user
            )

            for c in self.commitment.tblcompanycommitmentdetail_set.all():
                request_master.tblcompanyrequestdetail_set.create(
                    item=c.item,
                    amount=c.item.calculate_value(c.amount_factor,self.commitment.company)
                )

            # #request.send_email()

            self.request_next_interval_dt = to_date + datetime.timedelta(days=1)
            self.save()

class TblCompanyRequestMaster(LoggingModel):
    REQUEST_PAYMENT_NO_PAYMENT = "no"
    REQUEST_PAYMENT_PARTIAL_PAYMENT = "partial"
    REQUEST_PAYMENT_FULL_PAYMENT = "full"

    REQUEST_PAYMENT_CHOICES = {
        REQUEST_PAYMENT_NO_PAYMENT: _("no_payment"),
        REQUEST_PAYMENT_PARTIAL_PAYMENT: _("partial_payment"),
        REQUEST_PAYMENT_FULL_PAYMENT: _("full_payment"),
    }

    commitment  = models.ForeignKey(TblCompanyCommitmentMaster, on_delete=models.PROTECT,verbose_name=_("commitment"))    
    from_dt = models.DateField(_("from_dt"))
    to_dt = models.DateField(_("to_dt"))
    currency = models.CharField(_("currency"),max_length=10, choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_EURO)
    payment_state = models.CharField(_("payment_state"),max_length=10, choices=REQUEST_PAYMENT_CHOICES, default=REQUEST_PAYMENT_NO_PAYMENT)
    state = models.CharField(_("record_state"),max_length=10, choices=STATE_TYPE_CHOICES, default=STATE_TYPE_DRAFT)
    
    @property
    def total(self):   
        return self.tblcompanyrequestdetail_set.aggregate(total=Sum('amount'))['total'] or 0
    
    def __str__(self):
        return self.commitment.__str__()+" ("+str(self.total)+" "+CURRENCY_TYPE_CHOICES[self.currency]+")" #+" ("+str(self.from_dt)+" - "+str(self.to_dt)+") "
        
    def get_absolute_url(self): 
        return reverse('pa:request_show',args=[str(self.id)])                

    def sum_of_payment(self,exclude=0,confirmed_only=False):
        if self.state == STATE_TYPE_DRAFT:
            return 0
        
        sum = 0.0
        qs = self.tblcompanypaymentmaster_set
        if exclude:
            qs = qs.exclude(id=exclude)
        else:
            qs = qs.all()

        if confirmed_only:
            qs = qs.filter(state=STATE_TYPE_CONFIRM)

        for p in qs:
            if p.currency == self.currency:
                sum += p.total
            else:
                sum += p.total*p.exchange_rate

        return sum

    @property
    def sum_of_confirmed_payment(self,exclude=0):
        return self.sum_of_payment(exclude,confirmed_only=True)

    def update_payment_state(self):
        if self.state == STATE_TYPE_DRAFT:
            return
        sum = self.sum_of_payment(confirmed_only=True)

        if sum == 0:
            self.payment_state =  self.REQUEST_PAYMENT_NO_PAYMENT
        elif sum < self.total:
            self.payment_state =  self.REQUEST_PAYMENT_PARTIAL_PAYMENT
        else:
            self.payment_state =  self.REQUEST_PAYMENT_FULL_PAYMENT

        self.save()

        if self.payment_state == self.REQUEST_PAYMENT_FULL_PAYMENT:
            self.send_email()

    def send_email(self):
        if self.state == STATE_TYPE_DRAFT:
            return
        
        lang = TblCompanyProductionUserRole.objects.filter(company=self.commitment.company)[0].user.lang
        email = self.commitment.company.email
        url = 'https://'+Site.objects.get_current().domain+"/app"+reverse(settings.SHOW_REQUESTS_URL,args=[str(self.id)]) 
        logo_url = "https://"+Site.objects.get_current().domain+"/app/static/company_profile/img/smrc_logo.png"

        subject = None
        message = None
        
        if self.payment_state == self.REQUEST_PAYMENT_NO_PAYMENT:
            subject = _("Request wait for payment")+" ("+self.commitment.__str__()+")"
            message = render_to_string('pa/email/request_created_email_{0}.html'.format(lang),{
                'url':url,
                'logo':logo_url
            }) 
        elif self.payment_state == self.REQUEST_PAYMENT_FULL_PAYMENT:
            subject = _("Request paied")+" ("+self.commitment.__str__()+")"
            message = render_to_string('pa/email/request_paied_email_{0}.html'.format(lang),{
                'url':url,
                'logo':logo_url
            }) 
        
        if subject and message:
            send_mail(
                subject,
                strip_tags(message),
                None,
                [email],
                html_message=message,
                fail_silently=False,
            )        

    def clean(self):        
        if not hasattr(self,'commitment'):
            raise ValidationError(
                {"commitment":""}
            )
        
        qs = TblCompanyRequestMaster.objects.filter(
            commitment__company__id=self.commitment.company.id,
        )
        if self.id:
            qs = qs.exclude(id=self.id)

        if self.to_dt and self.from_dt:
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

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Financial request")
        verbose_name_plural = _("Financial requests")
        indexes = [
            models.Index(fields=["commitment"]),
        ]

class TblCompanyRequestDetail(models.Model):
    def attachement_path(self, filename):
        company = self.request_master.commitment.company
        date = self.request_master.created_at
        return "company_{0}/requests/{1}/{2}".format(company.id,date, filename)    

    request_master  = models.ForeignKey(TblCompanyRequestMaster, on_delete=models.PROTECT)
    item  = models.ForeignKey(LkpItem, on_delete=models.PROTECT,verbose_name=_("financial item"))    
    amount = models.FloatField(_("amount"))
    attachement_file = models.FileField(_("attachement_file"),upload_to=attachement_path,blank=True)

    def get_commitment_item_amount(self):
        qs =  self.request_master.commitment.tblcompanycommitmentdetail_set \
               .filter(item=self.item)
        
        sum = 0
        for c in qs:
            sum += c.item.calculate_value(c.amount_factor,self.request_master.commitment.company)

        return sum
    
    def get_item_payed_amount(self):
        qs = TblCompanyPaymentDetail.objects \
            .filter(payment_master__request=self.request_master,item=self.item)
        
        sum = 0
        for c in qs:
            sum += c.amount

        return sum

    def clean(self):
        if not hasattr(self,"request_master") or not hasattr(self.request_master,"commitment"):
            return
        
        if not self.id and self.request_master.state == STATE_TYPE_CONFIRM:
            raise ValidationError(
                {"item":_("request already confirmed!")}
            )
        
        commitment_item_amount = self.get_commitment_item_amount()

        if commitment_item_amount > 0 and self.amount != commitment_item_amount:
            raise ValidationError(
                {"amount":_("request amount should match commitment amount: ")+str(commitment_item_amount)}
            )
        
class TblCompanyRequestReceive(models.Model):
    request_master  = models.ForeignKey(TblCompanyRequestMaster, on_delete=models.PROTECT)
    receive_dt = models.DateField(_("receive_dt"))
    receiver_name = models.CharField(_("receiver_name"),max_length=50)

class TblCompanyPaymentMaster(LoggingModel):
    def attachement_path(self, filename):
        company = self.request.commitment.company
        date = self.payment_dt
        return "company_{0}/exchange_rate/{1}/{2}".format(company.id,date, filename)    

    request  = models.ForeignKey(TblCompanyRequestMaster, on_delete=models.PROTECT,verbose_name=_("request"))    
    payment_dt = models.DateField(_("payment_dt"))
    currency = models.CharField(_("currency"),max_length=10, choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_EURO)
    exchange_rate = models.FloatField(_("exchange_rate"),validators=[validate_positive],default=1)
    exchange_attachement_file = models.FileField(_("exchange_attachement_file"),upload_to=attachement_path,blank=True)
    state = models.CharField(_("record_state"),max_length=10, choices=STATE_TYPE_CHOICES, default=STATE_TYPE_DRAFT)
    
    @property
    def total(self):   
        return self.tblcompanypaymentdetail_set.aggregate(total=Sum('amount'))['total'] or 0

    def __str__(self):
        return _("Financial payment") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('pa:payment_show',args=[str(self.id)])             

    def clean(self):
        if self.currency == self.request.currency and self.exchange_rate != 1:
            raise ValidationError(
                {"exchange_rate":_("payment currency equal to request currency")}
            )
        elif self.currency != self.request.currency and not self.exchange_attachement_file:
            raise ValidationError(
                {"exchange_attachement_file":_("attach document")}
            )
        # sum = self.request.sum_of_payment(exclude=self.id)
        # if self.currency == self.request.currency:
        #     sum += self.total
        # else:
        #     sum += self.total*self.exchange_rate

        # if sum > self.request.total:
        #     raise ValidationError(
        #         {"amount":_("sum of payments more than request amount: ")+str(self.request.amount)+ " "+CURRENCY_TYPE_CHOICES[self.request.currency]}
        #     )

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Financial payment")
        verbose_name_plural = _("Financial payments")
        indexes = [
            models.Index(fields=["request"]),
        ]

class TblCompanyPaymentDetail(models.Model):
    def attachement_path(self, filename):
        company = self.payment_master.request.commitment.company
        date = self.payment_master.payment_dt
        return "company_{0}/payments/{1}/{2}".format(company.id,date, filename)    

    payment_master  = models.ForeignKey(TblCompanyPaymentMaster, on_delete=models.PROTECT)
    item  = models.ForeignKey(LkpItem, on_delete=models.PROTECT,verbose_name=_("financial item"))    
    amount = models.FloatField(_("amount"))
    attachement_file = models.FileField(_("attachement_file"),upload_to=attachement_path,blank=True)

    def get_request_item_amount(self):
        if not hasattr(self.payment_master,"request"):
            return -1
        
        return self.payment_master.exchange_rate * (self.payment_master.request.tblcompanyrequestdetail_set \
               .filter(item=self.item) \
               .aggregate(total=Sum('amount'))['total'] or 0)
    
    def get_payment_item_total(self,exclude=0):
        if not hasattr(self.payment_master,"request"):
            return -1

        sum =0
        qs = TblCompanyPaymentDetail.objects \
                .filter(payment_master__request=self.payment_master.request) \
                .exclude(id=exclude) \
                .filter(item=self.item)
        for p in qs:
            sum += p.payment_master.exchange_rate*p.amount

        return sum
    
    def clean(self):
        if not hasattr(self.payment_master,"request"):
            return 
        
        if not self.id and self.payment_master.state == STATE_TYPE_CONFIRM:
            raise ValidationError(
                {"item":_("payment already confirmed!")}
            )
        request_item_amount = self.get_request_item_amount()
        
        payment_id = self.id or 0
        payment_item_total_amount = self.amount or 0
        payment_item_total_amount += self.get_payment_item_total(exclude=payment_id)

        if request_item_amount == 0:
            raise ValidationError(
                {"item":_("item not exists in request")}
            )
        if payment_item_total_amount > request_item_amount:
            raise ValidationError(
                {"amount":_("sum of payments more than request amount: ")+" "+str(request_item_amount)+ "/" +str(payment_item_total_amount)+ " "+CURRENCY_TYPE_CHOICES[self.payment_master.request.currency]}
            )

class LkpPaymentMethod(models.Model):
    name = models.CharField(_("payment_method_name"),max_length=25)

    class Meta:
        ordering = ["id"]
        verbose_name = _("Payment method")
        verbose_name_plural = _("Payment method")

    def __str__(self):
        return self.name

class TblCompanyPaymentMethod(models.Model):
    def attachement_path(self, filename):
        company = self.payment_master.request.commitment.company
        date = self.payment_master.payment_dt
        return "company_{0}/payments/{1}/{2}".format(company.id,date, filename)    

    payment_master  = models.ForeignKey(TblCompanyPaymentMaster, on_delete=models.PROTECT)
    amount = models.FloatField(_("amount"))
    method  = models.ForeignKey(LkpPaymentMethod, on_delete=models.PROTECT,verbose_name=_("Payment method"))    
    ref_key = models.CharField(_("reference_key"),max_length=50)
    attachement_file = models.FileField(_("attachement_file"),upload_to=attachement_path)

    # def clean(self):
    #     if self.ref_key and not self.attachement_file:
    #         raise ValidationError(
    #             {"attachement_file":_("attach document")}
    #         )
