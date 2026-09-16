from django import forms
from django.utils.translation import gettext_lazy as _
from maintenance.models import (
    MaintenanceRequest, CompletionReport, ServiceRating,
    SparePart, StockMovement, FaultCategory, Floor, Apartment, TechnicalTechnician
)


def get_employee_info(user):
    if not user or not user.is_authenticated:
        return None, {}

    try:
        from hr.models import EmployeeBasic

        emp = None
        if getattr(user, 'email', None):
            emp = EmployeeBasic.objects.filter(email__iexact=user.email).first()

        if not emp and getattr(user, 'username', None):
            if str(user.username).isdigit():
                emp = EmployeeBasic.objects.filter(code=int(user.username)).first()

        if not emp:
            full_name = user.get_full_name()
            if full_name and len(full_name.strip()) > 3:
                emp = EmployeeBasic.objects.filter(name__icontains=full_name.strip()).first()

        if emp:
            gen_dept_name = ''
            if emp.edara_3ama:
                gen_dept_name = getattr(emp.edara_3ama, 'name', str(emp.edara_3ama))

            dept_name = ''
            if emp.edara_far3ia:
                dept_name = getattr(emp.edara_far3ia, 'name', str(emp.edara_far3ia))
            elif emp.gisim:
                dept_name = getattr(emp.gisim, 'name', str(emp.gisim))
            elif emp.hikal_wazifi:
                dept_name = str(emp.hikal_wazifi)

            return emp, {
                'employee_name': emp.name,
                'general_dept': gen_dept_name,
                'department': dept_name,
            }
    except Exception:
        pass

    return None, {}


class MaintenanceRequestForm(forms.ModelForm):
    """نموذج تقديم طلب صيانة"""

    class Meta:
        model  = MaintenanceRequest
        fields = [
            'employee_name', 'general_dept', 'department',
            'floor', 'apartment', 'location',
            'fault_category', 'fault_description', 'priority',
            'requires_safety_permit',
        ]
        widgets = {
            'employee_name':    forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': _('الاسم الرباعي')
            }),
            'general_dept':     forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': _('مثال: الإدارة العامة للشؤون المالية')
            }),
            'department':       forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': _('مثال: قسم الحسابات')
            }),
            'floor':            forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'id': 'id_floor',
            }),
            'apartment':        forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'id': 'id_apartment',
            }),
            'location':         forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': _('ملاحظات إضافية على الموقع (اختياري)')
            }),
            'fault_category':   forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'id': 'id_fault_category',
            }),
            'fault_description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': _('وصف إضافي للمشكلة (مطلوب)')
            }),
            'priority':         forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'requires_safety_permit': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-warning',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        is_admin = False
        is_tech  = False
        if self.user:
            groups = list(self.user.groups.values_list('name', flat=True))
            is_admin = self.user.is_superuser or 'maintenance_admin' in groups
            is_tech  = any(g in groups for g in [
                'maintenance_elec', 'maintenance_air_cond', 'maintenance_mech', 'maintenance_const'
            ])

        self.is_admin = is_admin

        # Require fault description
        self.fields['fault_description'].required = True

        # Dropdowns for Floor and Apartment
        self.fields['floor'].queryset = Floor.objects.all().order_by('order', 'name')
        self.fields['floor'].required = False
        self.fields['apartment'].required = False

        if 'floor' in self.data:
            try:
                floor_id = int(self.data.get('floor'))
                self.fields['apartment'].queryset = Apartment.objects.filter(floor_id=floor_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['apartment'].queryset = Apartment.objects.none()
        elif self.instance and self.instance.pk and self.instance.floor:
            self.fields['apartment'].queryset = self.instance.floor.apartments.order_by('name')
        else:
            self.fields['apartment'].queryset = Apartment.objects.none()

        fault_cats = FaultCategory.objects.filter(is_active=True).select_related('unit')
        if not is_admin:
            fault_cats = fault_cats.filter(
                requires_safety_permit=False,
                unit__requires_safety_permit=False
            ).exclude(unit__code='SAFETY')

        self.fields['fault_category'].queryset = fault_cats.order_by('unit__code', 'order', 'name')

        # Hide the requires_safety_permit field from non-admin users
        if not is_admin:
            self.fields.pop('requires_safety_permit', None)

        # Hide Priority from regular requesters (non-admin and non-technician)
        if not (is_admin or is_tech):
            self.fields.pop('priority', None)

        self.employee_in_structure = False
        self.employee_obj = None

        if self.user:
            emp_obj, emp_data = get_employee_info(self.user)
            if emp_obj:
                self.employee_obj = emp_obj
                self.employee_in_structure = True

                if not self.is_bound or not self.data.get('employee_name'):
                    self.initial['employee_name'] = emp_data.get('employee_name', '')
                if not self.is_bound or not self.data.get('general_dept'):
                    self.initial['general_dept'] = emp_data.get('general_dept', '')
                if not self.is_bound or not self.data.get('department'):
                    self.initial['department'] = emp_data.get('department', '')

                for field in ['employee_name', 'general_dept', 'department']:
                    if field in self.fields:
                        self.fields[field].widget.attrs['readonly'] = True
                        cls = self.fields[field].widget.attrs.get('class', '')
                        self.fields[field].widget.attrs['class'] = cls + ' bg-base-200 cursor-not-allowed font-semibold text-gray-700'
            else:
                self.employee_in_structure = False
                if not self.is_bound and not self.initial.get('employee_name'):
                    full_name = self.user.get_full_name()
                    if full_name:
                        self.initial['employee_name'] = full_name

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.requester = self.user

        if self.employee_obj:
            _, emp_data = get_employee_info(self.user)
            if emp_data.get('employee_name'):
                instance.employee_name = emp_data['employee_name']
            if emp_data.get('general_dept'):
                instance.general_dept = emp_data['general_dept']
            if emp_data.get('department'):
                instance.department = emp_data['department']
            instance.employee = self.employee_obj

        # Construct location string automatically from floor and apartment if available
        loc_parts = []
        if instance.floor:
            loc_parts.append(instance.floor.name)
        if instance.apartment:
            loc_parts.append(instance.apartment.name)
        
        extra_loc = instance.location.strip() if instance.location else ''
        if loc_parts:
            computed_loc = " — ".join(loc_parts)
            if extra_loc and extra_loc != computed_loc:
                computed_loc += f" ({extra_loc})"
            instance.location = computed_loc
        elif not extra_loc:
            instance.location = "غير محدد"

        if commit:
            instance.save()
        return instance


class EmployeeRequestForm(MaintenanceRequestForm):
    pass


class TechnicalTechnicianForm(forms.ModelForm):
    class Meta:
        model  = TechnicalTechnician
        fields = ['name', 'phone', 'unit', 'specialty', 'is_active']
        widgets = {
            'name':      forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': _('اسم الفني التقني')}),
            'phone':     forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': _('رقم الهاتف')}),
            'unit':      forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'specialty': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': _('التخصص أو الملاحظات (اختياري)')}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-primary'}),
        }


class CompletionReportForm(forms.ModelForm):

    class Meta:
        model  = CompletionReport
        fields = ['work_done', 'root_cause', 'recommendations']
        widgets = {
            'work_done':       forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': _('صف العمل الذي تم إنجازه بالتفصيل')
            }),
            'root_cause':      forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': _('ما السبب الجذري للعطل؟')
            }),
            'recommendations': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': _('توصيات لمنع تكرار العطل (اختياري)')
            }),
        }


class SparePartUsageForm(forms.Form):
    spare_part = forms.ModelChoiceField(
        queryset=SparePart.objects.filter(is_active=True, quantity_in_stock__gt=0),
        required=False,
        label=_('القطعة المستهلكة'),
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        required=False,
        initial=1,
        label=_('الكمية'),
        widget=forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': '1'})
    )


class ServiceRatingForm(forms.ModelForm):
    

    class Meta:
        model  = ServiceRating
        fields = ['rating', 'comment']
        widgets = {
            'rating':  forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'comment': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': _('تعليقك على الخدمة المقدمة (اختياري)')
            }),
        }


class SparePartForm(forms.ModelForm):

    class Meta:
        model  = SparePart
        fields = ['sku', 'name', 'unit', 'description', 'unit_of_measure',
                  'quantity_in_stock', 'reorder_point', 'is_active']
        widgets = {
            'sku':              forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'name':             forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'unit':             forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'description':      forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'unit_of_measure':  forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': '0'}),
            'reorder_point':    forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': '0'}),
        }


class StockMovementForm(forms.ModelForm):

    class Meta:
        model  = StockMovement
        fields = ['spare_part', 'movement_type', 'quantity', 'maintenance_request', 'notes']
        widgets = {
            'spare_part':           forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'movement_type':        forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'quantity':             forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'min': '1'}),
            'maintenance_request':  forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'notes':                forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['maintenance_request'].required = False
        self.fields['maintenance_request'].queryset = (
            MaintenanceRequest.objects.filter(
                status__in=['in_progress', 'completed']
            ).order_by('-created_at')
        )


class RequestFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', _('كل الحالات'))] + MaintenanceRequest.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'select select-bordered select-sm'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered input-sm',
            'placeholder': _('بحث بالاسم أو القسم أو رقم الطلب...')
        })
    )
    unit = forms.CharField(required=False, widget=forms.HiddenInput())
    priority = forms.ChoiceField(
        choices=[('', _('كل الأولويات'))] + MaintenanceRequest.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'select select-bordered select-sm'})
    )


class SafetyPermitForm(forms.ModelForm):
    """نموذج تعبئة استمارة السلامة والصحة المهنية (الفني / المسؤول)"""
    HAZARDOUS_CHOICES = [
        ('welding', _('أعمال لحام وقص ومعادن')),
        ('fumes', _('أبخرة وغازات مواد كيميائية')),
        ('heights', _('العمل في أماكن مرتفعة (سقالات / سلالم)')),
        ('construction', _('أعمال بناء جديد وتكسير وصيانة هيكلية')),
        ('lifting', _('رفع يدوي وأحمال ثقيلة')),
        ('other', _('أخرى (تُحدد أدناه)')),
    ]

    SITE_PREP_CHOICES = [
        ('extinguisher', _('طفاية حريق متوفرة وجاهزة')),
        ('ventilation', _('وسائل تهوية مناسبة')),
        ('exits', _('مخارج طوارئ واضحة وغير مسدودة')),
        ('electrical_isolation', _('عزل وتأمين التيار الكهربائي / مصادر الطاقة')),
        ('communication', _('وسائل اتصال طوارئ متوفرة')),
        ('flammable', _('إبعاد وشحن المواد القابلة للإشتعال')),
        ('other', _('تجهيزات أخرى')),
    ]

    PPE_CHOICES = [
        ('shoes', _('حذاء السلامة (Safety Shoes)')),
        ('helmet', _('خوذة الرأس (Safety Helmet)')),
        ('mask', _('الكمامة / واقي التنفس')),
        ('overall', _('الأبرول / بدلة العمل')),
        ('ear_protection', _('واقي الأذن (Ear Muffs/Plugs)')),
        ('glasses', _('نظارات السلامة / الواقي الشفاف')),
        ('gloves', _('القفازات / الجوانتي (Safety Gloves)')),
    ]

    hazardous_activities = forms.MultipleChoiceField(
        choices=HAZARDOUS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label=_('7. الأنشطة الخطرة المرتبطة بالعمل'),
        required=False
    )
    site_preparations = forms.MultipleChoiceField(
        choices=SITE_PREP_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label=_('9. تجهيزات المكان وإجراءات الطوارئ'),
        required=False
    )
    ppe_equipment = forms.MultipleChoiceField(
        choices=PPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label=_('10. مهمات ومعدات الحماية الشخصية المطلوبة (PPE)'),
        required=False
    )

    class Meta:
        from maintenance.models import SafetyPermit
        model = SafetyPermit
        fields = [
            'work_description', 'start_time', 'end_time',
            'responsible_person_name', 'responsible_person_job',
            'assigned_technicians',
            'hazardous_activities_other', 'control_measures',
            'site_preparations_other',
        ]
        widgets = {
            'work_description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': _('وصف دقيق لطبيعة وحجم العمل المخطط تنفيذه...')
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'datetime-local'
            }),
            'responsible_person_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': _('اسم الشخص القائم/المسؤول عن التنفيذ')
            }),
            'responsible_person_job': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': _('المسمى الوظيفي')
            }),
            'hazardous_activities_other': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': _('حدد أنشطة خطرة أخرى إن وجدت...')
            }),
            'control_measures': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': _('طرق التحكم والوقاية والإجراءات الاحترازية المتخذة...')
            }),
            'site_preparations_other': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': _('تجهيزات مكان أخرى إن وجدت...')
            }),
        }

    # المجموعات التقنية فقط (الفنيون) — السلامة مستثناة دائماً
    TECHNICIAN_GROUPS = [
        'maintenance_elec',
        'maintenance_air_cond',
        'maintenance_mech',
        'maintenance_const',
    ]

    def __init__(self, *args, **kwargs):
        unit = kwargs.pop('unit', None)
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # إذا كانت الوحدة محددة ولديها group_name من المجموعات التقنية — فلتر بها
        # وإلا جلب جميع الفنيين من المجموعات التقنية الأربع فقط
        if unit and unit.group_name and unit.group_name in self.TECHNICIAN_GROUPS:
            qs = User.objects.filter(
                groups__name=unit.group_name
            ).distinct().order_by('first_name', 'last_name', 'username')
        else:
            qs = User.objects.filter(
                groups__name__in=self.TECHNICIAN_GROUPS
            ).distinct().order_by('first_name', 'last_name', 'username')

        self.fields['assigned_technicians'] = TechnicianChoiceField(
            queryset=qs,
            widget=forms.CheckboxSelectMultiple,
            label=_('الفنيون المكلفون / المشاركون بالمهمة'),
            required=False
        )

        if self.instance and self.instance.pk:
            if isinstance(self.instance.hazardous_activities, list):
                self.fields['hazardous_activities'].initial = self.instance.hazardous_activities
            if isinstance(self.instance.site_preparations, list):
                self.fields['site_preparations'].initial = self.instance.site_preparations
            if isinstance(self.instance.ppe_equipment, list):
                self.fields['ppe_equipment'].initial = self.instance.ppe_equipment
            self.fields['assigned_technicians'].initial = self.instance.assigned_technicians.all()


class TechnicianChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        from maintenance.templatetags.maintenance_tags import user_display_name
        return user_display_name(obj)



class SafetyPermitApprovalForm(forms.Form):
    """نموذج اعتماد وموافقة موظف قسم السلامة الداخلية"""
    permit_duration = forms.CharField(
        label=_('4. مدة التصريح الصادرة من السلامة'),
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': _('مثال: 4 ساعات / يوم واحد / حتى 2026/09/10 الساعة 02:00 مساءً')
        }),
        help_text=_('من صلاحيات قسم السلامة إدخال قيمة هذا الحقل حكراً')
    )
    safety_notes = forms.CharField(
        label=_('توصيات وملاحظات قسم السلامة المهنية'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'textarea textarea-bordered w-full',
            'rows': 3,
            'placeholder': _('توصيات السلامة الواجب اتباعها قبل وأثناء العمل...')
        })
    )
    decision = forms.ChoiceField(
        label=_('القرار النهائي'),
        choices=[
            ('approve', _('✅ موافقة على تصريح السلامة وتسمح ببدء العمل')),
            ('reject',  _('❌ رفض التصريح لحين استكمال شروط السلامة')),
        ],
        widget=forms.Select(attrs={'class': 'select select-bordered w-full font-bold'})
    )

