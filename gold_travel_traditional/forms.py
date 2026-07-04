from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from gold_travel_traditional.models import AppMoveGoldTraditional, GoldTravelTraditionalUser, GoldTravelTraditionalUserJihatAlaisdar, GoldTravelTraditionalUserJihatTarhil, LkpJihatAlaisdar, LkpJihatAltarhil, MeltBatch, Sale

UserModel = get_user_model()

class GoldTravelTraditionalUserForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=UserModel.objects.filter(groups__name__in=['gold_travel_traditional_state',]),
        label=_("user")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user' in self.fields:
            self.fields['user'].label_from_instance = lambda obj: f"{obj.get_full_name()} ({obj.username})"

    class Meta:
        model = GoldTravelTraditionalUser    
        fields = ["user","name","state","user_type"] 

class GoldTravelTraditionalUserJihatAlaisdarForm(forms.ModelForm):
    jihat_alaisdar = forms.ModelChoiceField(queryset=LkpJihatAlaisdar.objects.none(), label=_("جهة الإصدار"))
    allowed_state = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.filter(state=self.allowed_state)

    class Meta:
        model = GoldTravelTraditionalUserJihatAlaisdar   
        fields = ["jihat_alaisdar",] 

class GoldTravelTraditionalUserJihatTarhilForm(forms.ModelForm):
    wijhat_altarhil = forms.ModelChoiceField(queryset=LkpJihatAltarhil.objects.none(), label=_("جهة الوصول"))
    allowed_state = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.all() #filter(state=self.allowed_state)

    class Meta:
        model = GoldTravelTraditionalUserJihatTarhil   
        fields = ["wijhat_altarhil",] 

class AppMoveGoldTraditionalAddForm(forms.ModelForm):
    issue_date = forms.DateField(label=_("issue_date"), disabled=True, required=True)
    jihat_alaisdar = forms.ModelChoiceField(queryset=LkpJihatAlaisdar.objects.none(), label=_("جهة الإصدار"))
    wijhat_altarhil = forms.ModelChoiceField(queryset=LkpJihatAltarhil.objects.none(), label=_("جهة الوصول"))
    almushtari_name = forms.CharField(label=_("almushtari_name"), max_length=150, disabled=True, required=False)
    
    user = None
    allowed_state = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['issue_date'].initial = timezone.now().date()

        if self.user: # and not self.user.is_superuser
            try:
                gold_user = self.user.gold_travel_traditional
                if gold_user.is_state_manager or gold_user.is_state_viewer:
                    self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.all()
                    self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.all()
                else:
                    if gold_user.is_alaisdar_user:
                        self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.filter(
                            id__in=gold_user.goldtraveltraditionaluserjihatalaisdar_set.values_list('jihat_alaisdar', flat=True)
                        )
                    else:
                        self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.none()
                    
                    self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.filter(
                        id__in=gold_user.goldtraveltraditionaluserjihattarhil_set.values_list('wijhat_altarhil', flat=True)
                    )
            except:
                self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.none()
                self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.none()
        else:
            self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.all()
            self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.all()

    class Meta:
        model = AppMoveGoldTraditional    
        fields = ["issue_date","almustafid_name","almustafid_phone","almustafid_identity_type","almustafid_identity","almustafid_identity_attachement","jihat_alaisdar","wijhat_altarhil","attachement_file","state","source_state"] 

    def clean_attachement_file(self):
        from django.core.exceptions import ValidationError
        file = self.cleaned_data.get('attachement_file')
        if file:
            # Check file extension
            ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else ''
            if ext not in ('jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'):
                raise ValidationError(_('يجب رفع صورة بصيغة JPG, PNG, GIF, WEBP أو BMP فقط'))
            # Verify it's a valid image
            from PIL import Image
            try:
                img = Image.open(file)
                img.verify()
                file.seek(0)
            except Exception:
                raise ValidationError(_('الملف المرفوع ليس صورة صالحة'))
        return file

    def clean_almustafid_identity_attachement(self):
        from django.core.exceptions import ValidationError
        file = self.cleaned_data.get('almustafid_identity_attachement')
        if file:
            ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else ''
            if ext not in ('jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'):
                raise ValidationError(_('يجب رفع صورة بصيغة JPG, PNG, GIF, WEBP أو BMP فقط'))
            from PIL import Image
            try:
                img = Image.open(file)
                img.verify()
                file.seek(0)
            except Exception:
                raise ValidationError(_('الملف المرفوع ليس صورة صالحة'))
        return file
        
class AppMoveGoldTraditionalMeltForm(forms.Form):
    batch_choice = forms.ChoiceField(
        label=_('نوع الدفعة'),
        choices=[('new', _('دفعة جديدة')), ('existing', _('إضافة لدفعة موجودة'))],
        initial='new',
        widget=forms.RadioSelect()
    )
    existing_batch = forms.ModelChoiceField(
        queryset=MeltBatch.objects.none(),
        label=_('اختر الدفعة'),
        required=False
    )
    melt_date = forms.DateField(
        label=_('تاريخ الصهر'),
        initial=timezone.now().date(),
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'vDateField'})
    )
    melt_workshop = forms.CharField(label=_('ورشة الصهر'), max_length=150, required=True)
    standardization_lab = forms.CharField(label=_('مختبر المعايرة'), max_length=150, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # New/Existing fields only required if that choice is selected
        self.fields['melt_date'].required = False
        self.fields['melt_workshop'].required = False
        self.fields['standardization_lab'].required = False

    def clean(self):
        cleaned = super().clean()
        choice = cleaned.get('batch_choice')
        if choice == 'new':
            if not cleaned.get('melt_date'):
                self.add_error('melt_date', _('This field is required.'))
            if not cleaned.get('melt_workshop'):
                self.add_error('melt_workshop', _('This field is required.'))
            if not cleaned.get('standardization_lab'):
                self.add_error('standardization_lab', _('This field is required.'))
        elif choice == 'existing':
            if not cleaned.get('existing_batch'):
                self.add_error('existing_batch', _('Please select a batch.'))
        return cleaned

class AppMoveGoldTraditionalSaleForm(forms.Form):
    batch_choice = forms.ChoiceField(
        label=_('نوع الفاتورة'),
        choices=[('new', _('فاتورة جديدة')), ('existing', _('إضافة لفاتورة موجودة'))],
        initial='new',
        widget=forms.RadioSelect()
    )
    existing_sale = forms.ModelChoiceField(
        queryset=Sale.objects.none(),
        label=_('اختر الفاتورة'),
        required=False
    )
    sale_date = forms.DateField(
        label=_('تاريخ البيع'),
        initial=timezone.now().date(),
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'vDateField'})
    )
    buyer = forms.ModelChoiceField(
        queryset=None,
        label=_('المشتري'),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from gold_travel.models import LkpOwner
        self.fields['buyer'].queryset = LkpOwner.objects.filter(state=LkpOwner.STATE_ACTIVE)
        self.fields['sale_date'].required = False
        self.fields['buyer'].required = False

    def clean(self):
        cleaned = super().clean()
        choice = cleaned.get('batch_choice')
        if choice == 'new':
            if not cleaned.get('sale_date'):
                self.add_error('sale_date', _('This field is required.'))
            if not cleaned.get('buyer'):
                self.add_error('buyer', _('This field is required.'))
        elif choice == 'existing':
            if not cleaned.get('existing_sale'):
                self.add_error('existing_sale', _('Please select a sale.'))
        return cleaned

class AppMoveGoldTraditionalRenewForm(forms.ModelForm):
    jihat_alaisdar = forms.ModelChoiceField(queryset=LkpJihatAlaisdar.objects.none(), label=_("جهة الإصدار"))
    wijhat_altarhil = forms.ModelChoiceField(queryset=LkpJihatAltarhil.objects.none(), label=_("جهة الوصول"))

    user = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.user and not self.user.is_superuser:
            try:
                gold_user = self.user.gold_travel_traditional
                if gold_user.is_state_manager or gold_user.is_state_viewer:
                    self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.all()
                    self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.all()
                else:
                    if gold_user.is_alaisdar_user:
                        self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.filter(
                            id__in=gold_user.goldtraveltraditionaluserjihatalaisdar_set.values_list('jihat_alaisdar', flat=True)
                        )
                    else:
                        self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.none()
                    
                    self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.filter(
                        id__in=gold_user.goldtraveltraditionaluserjihattarhil_set.values_list('wijhat_altarhil', flat=True)
                    )
            except:
                self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.none()
                self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.none()
        else:
            self.fields["jihat_alaisdar"].queryset = LkpJihatAlaisdar.objects.all()
            self.fields["wijhat_altarhil"].queryset = LkpJihatAltarhil.objects.all()

    class Meta:
        model = AppMoveGoldTraditional    
        fields = ["code","issue_date","almustafid_name","almustafid_phone","almustafid_identity_type","almustafid_identity","jihat_alaisdar","wijhat_altarhil",] 
        # widgets = {
        #     'issue_date': admin.widgets.AdminDateWidget(),
        #     'jihat_alaisdar': forms.Select(),
        #     'gold_weight_in_gram': forms.TextInput(),
        # }
