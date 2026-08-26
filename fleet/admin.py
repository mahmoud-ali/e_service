from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum

from . import models


class LogMixin(admin.ModelAdmin):
    """
    A base ModelAdmin for models that inherit from LoggingModel.
    It makes the logging fields readonly and sets the user on save.
    """
    # readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        Given an inline formset, save it to the database, setting the
        user on each object.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            # Check if the model is an instance of LoggingModel
            # Note: models.LoggingModel is abstract, but we can check the attributes
            if hasattr(instance, 'created_by_id'):
                if not instance.pk:
                    instance.created_by = request.user
                instance.updated_by = request.user
            instance.save()
        formset.save_m2m()
        
        for obj in formset.deleted_objects:
            obj.delete()

class VehicleCertificateInline(admin.TabularInline):
    model = models.VehicleCertificate
    fields = ('cert_type','start_date','end_date','attachments','notes')
    extra = 0
    # readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')


class VehicleAssignmentInline(admin.TabularInline):
    model = models.VehicleAssignment
    extra = 0
    # readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')


class VehicleDriverInline(admin.TabularInline):
    model = models.VehicleDriver
    autocomplete_fields = ["driver"]
    extra = 0
    # readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

class VehicleGPSDeviceInline(admin.TabularInline):
    model = models.VehicleGPSDevice
    autocomplete_fields = ["vehicle",]
    # fields = ('cert_type','start_date','end_date','attachments','notes')
    extra = 0
    # readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

@admin.register(models.Vehicle)
class VehicleAdmin(LogMixin):
    list_display = ('model', 'year', 'license_plate', 'status', 'fuel_type',) #,'last_position'
    list_filter = ('status', 'fuel_type','year', 'model__make','model__name')
    search_fields = ('license_plate', 'model__name', 'model__make__name', 'year')
    inlines = [
        VehicleCertificateInline,
        VehicleAssignmentInline,
        VehicleDriverInline,
        VehicleGPSDeviceInline,
    ]

    @admin.display(description="اخر موقع")
    def last_position(self, obj):
        try:
            tc_device_pos_id = models.VehicleGPSDevice.objects.get(vehicle=obj).gps.positionid
            tc_position = models.TcPositions.objects.get(id=tc_device_pos_id)
            return format_html(f'<a target="_blank" href="https://www.google.com/maps?q={tc_position.latitude},{tc_position.longitude}">الخريطة ({tc_position.servertime})</a>')
        except Exception as e:
            # print('****',e)
            pass

        return ''

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if request.GET.get('mission_only'):
            queryset = queryset.filter(vehicleassignment__status='missions', vehicleassignment__end_date__isnull=True).distinct()
            use_distinct = True
        return queryset, use_distinct


@admin.register(models.VehicleMake)
class VehicleMakeAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(models.VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'make')
    list_filter = ('make',)
    search_fields = ('name', 'make__name')

@admin.register(models.Driver)
class DriverAdmin(LogMixin):
    list_display = ('name', 'license_no', 'license_type', 'expiry_date',)
    search_fields = ('name', 'license_no')

    list_filter = ('license_type',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        vehicle_id = request.GET.get('vehicle_id')
        if vehicle_id:
            queryset = queryset.filter(vehicledriver__vehicle_id=vehicle_id, vehicledriver__end_date__isnull=True)
        return queryset, use_distinct

@admin.register(models.VehicleAssignment)
class VehicleAssignmentAdmin(LogMixin):
    list_display = ('vehicle', 'assign_to', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'vehicle__model__make','vehicle__model','vehicle__year')
    search_fields = ('assign_to', 'vehicle__license_plate')
    autocomplete_fields = ["vehicle"]

@admin.register(models.TcDevices)
class TcDevicesAdmin(LogMixin):
    fields = ('name', 'uniqueid', )
    list_display = ('name', 'uniqueid', )
    search_fields = ('name', 'uniqueid')

    verbose_name= "قائمة اجهزة التتبع"
    

class MissionAttachmentInline(admin.TabularInline):
    model = models.MissionAttachment
    fields = ('file', 'description')
    extra = 1
    verbose_name = "مرفق"
    verbose_name_plural = "المرفقات"


class MissionVehicleInline(admin.TabularInline):
    model = models.MissionVehicle
    fields = ('assignment',)
    #autocomplete_fields = ["assignment"]
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assignment":
            # Filter assignments for vehicles that have status 'missions'
            kwargs["queryset"] = models.VehicleDriver.objects.filter(
                vehicle__vehicleassignment__status='missions',
                vehicle__vehicleassignment__end_date__isnull=True,
                end_date__isnull=True # Only active driver assignments
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(models.Mission)
class MissionAdmin(LogMixin):
    change_form_template = 'admin/fleet/mission/change_form.html'
    fieldsets = (
        (None, {
            'fields': ('destination', 'requested_by', 'no_of_vehicles')
        }),
        ('التواريخ', {
            'fields': (('planned_start_date', 'actual_start_date'), 'no_of_days', ('planned_end_date', 'actual_end_date'))
        }),
        ('تمديد المأمورية', {
            'fields': ('is_extended', 'extension_days', ('extended_planned_end_date', 'extended_actual_end_date'))
        }),
        ('قطع المأمورية', {
            'fields': ('termination_date',),
            'classes': ('collapse',),
            'description': 'تحديد هذا التاريخ يقطع المأمورية ويجعلها منتهية اعتباراً من هذا التاريخ، ويصبح بإمكان السائق والمركبة الإسناد في مأمورية جديدة.',
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
    )
    list_display = ('requested_by', 'destination', 'no_of_vehicles', 'no_of_days', 'planned_start_date', 'effective_end_display', 'actual_start_date', 'actual_end_date_display', 'termination_date', 'status_tag')
    list_filter = ('planned_start_date', 'planned_end_date', 'actual_end_date', 'termination_date', 'requested_by')
    search_fields = ('destination', 'requested_by', 'missionvehicle__assignment__driver__name', 'missionvehicle__assignment__vehicle__license_plate')
    readonly_fields = ('planned_end_date','actual_end_date','extended_planned_end_date','extended_actual_end_date')

    @admin.display(description="تاريخ الانتهاء")
    def effective_end_display(self, obj):
        if obj.is_extended and obj.extended_planned_end_date:
            return format_html('<b>{}</b> <span style="color:orange;">(ممدد)</span>', obj.extended_planned_end_date)
        return obj.planned_end_date

    @admin.display(description="تاريخ الانتهاء الفعلي", ordering='actual_end_date')
    def actual_end_date_display(self, obj):
        if obj.termination_date:
            return format_html('<b style="color:#c0392b;">{}</b> <span style="color:#c0392b;">(مقطوعة)</span>', obj.termination_date)
        if obj.actual_end_date:
            if obj.is_extended and obj.extended_actual_end_date:
                return format_html('<b>{}</b> <span style="color:orange;">(ممدد)</span>', obj.extended_actual_end_date)
            return obj.actual_end_date
        return format_html('<span style="color: green; font-weight: bold;">جارية</span>')

    @admin.display(description="حالة الانتهاء")
    def status_tag(self, obj):
        from django.utils import timezone
        today = timezone.now().date()

        start_date = obj.actual_start_date

        # إن لم تبدأ بعد
        if not start_date or start_date > today:
            return format_html('<span style="color: #0275d8; font-weight: bold;">لم تبدأ بعد</span>')

        # إن كانت مقطوعة
        if obj.termination_date:
            return format_html(
                '<span style="color: white; background-color: #c0392b; padding: 3px 10px; border-radius: 10px; font-weight: bold;">✂ مقطوعة {}</span>',
                obj.termination_date
            )

        # تحديد تاريخ النهاية الفعلي
        end_date = obj.effective_actual_end_date

        # إن انتهت
        if end_date and end_date < today:
            return format_html('<span style="color: #777; font-weight: bold;">منتهية</span>')

        # جارية مع تنبيهات
        if end_date:
            diff = (end_date - today).days
            if diff == 0:
                return format_html('<span style="color: white; background-color: #d9534f; padding: 3px 10px; border-radius: 10px; font-weight: bold;">تنتهي اليوم</span>')
            elif 0 < diff <= 2:
                return format_html('<span style="color: white; background-color: #f0ad4e; padding: 3px 10px; border-radius: 10px; font-weight: bold;">متبقي {} أيام</span>', diff)

        return format_html('<span style="color: green; font-weight: bold;">جارية</span>')

    @admin.display(description="المركبات")
    def get_vehicles(self, obj):
        vehicles = [str(mv.assignment.vehicle) for mv in obj.missionvehicle_set.all() if mv.assignment]
        if obj.vehicle: # Legacy
            vehicles.insert(0, str(obj.vehicle))
        return ", ".join(vehicles)
    # autocomplete_fields = ["vehicle","driver"]
    inlines = [MissionVehicleInline, MissionAttachmentInline]
 
class Media:
    js = ('fleet/js/mission_extension.js',)


class VehicleMaintenancePartInline(admin.TabularInline):
    model = models.VehicleMaintenancePart
    extra = 0

@admin.register(models.VehicleMaintenance)
class VehicleMaintenanceAdmin(LogMixin):
    list_display = ('vehicle', 'service_date','next_service_due','odometer_km', 'service_type', 'service_provider','service_total_cost')
    list_filter = ('vehicle__model__make','vehicle__model','vehicle__year','service_date', 'service_type','service_provider')
    search_fields = ('vehicle__license_plate',)
    autocomplete_fields = ["vehicle",]
    inlines = [
        VehicleMaintenancePartInline,
    ]



# @admin.register(models.VehicleCertificate)
# class VehicleCertificateAdmin(LogMixin):
#     list_display = ('vehicle', 'cert_type', 'start_date', 'end_date')
#     list_filter = ('cert_type', 'vehicle')
#     search_fields = ('vehicle__license_plate',)

@admin.register(models.VehicleDriver)
class VehicleDriverAdmin(LogMixin):
    list_display = ('vehicle', 'driver', 'start_date', 'end_date')
    search_fields = ('vehicle__license_plate', 'driver__name', 'vehicle__model__name')

# Register simple models without customization
# admin.site.register(models.VehicleFuelType)
# admin.site.register(models.VehicleStatus)
admin.site.register(models.DriverLicenseType)
admin.site.register(models.VehicleCertificateType)
# admin.site.register(models.ServiceType)
admin.site.register(models.ServiceProvider)
# admin.site.register(models.VehicleSparePart)

@admin.register(models.ServiceType)
class ServiceTypeAdmin(LogMixin):
    fieldsets = (
        (None, {
            "fields": (
                'name',
            ),
        }),
        ('الخدمة او الصيانة الدزرية', {
            "fields": (
                'periodic','no_of_days',
            ),
        }),
    )
    list_display = ('name', 'periodic','no_of_days',)
    list_filter = ('periodic',)
    search_fields = ('name',)


class FuelDistributionItemInline(admin.TabularInline):
    model = models.FuelDistributionItem
    extra = 0
    max_num = 0
    can_delete = False
    readonly_fields = ('is_external', 'beneficiary_name', 'card_number', 'email', 'department', 'job_title', 'petrol_liters', 'diesel_liters', 'amount', 'notes_signature')
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False



@admin.register(models.FuelMonthlyStatement)
class FuelMonthlyStatementAdmin(LogMixin):
    list_display = ('title', 'month', 'year', 'statement_date', 'total_beneficiaries', 'total_petrol_liters', 'total_diesel_liters', 'total_amount', 'generate_btn', 'print_btn')
    list_filter = ('year', 'month')
    search_fields = ('title', 'notes')
    inlines = [FuelDistributionItemInline]
    change_form_template = 'admin/fleet/fuelmonthlystatement/change_form.html'
    readonly_fields = ('petrol_price_per_gallon_display', 'diesel_price_per_gallon_display')
    fieldsets = (
        (None, {
            'fields': ('title', ('month', 'year'), 'statement_date')
        }),
        ('أسعار الوقود وحساب سعر الجالون', {
            'fields': (
                ('petrol_price_per_liter', 'petrol_price_per_gallon_display'),
                ('diesel_price_per_liter', 'diesel_price_per_gallon_display'),
            ),
            'description': 'أدخل سعر اللتر وسيتم حساب سعر الجالون'
        }),
        ('ملاحظات', {
            'fields': ('notes',)
        }),
    )

    @admin.display(description='سعر جالون البنزين (جنيه)')
    def petrol_price_per_gallon_display(self, obj):
        if not obj or not obj.petrol_price_per_liter:
            return "0.00 جنيه"
        return f"{obj.petrol_price_per_gallon} جنيه (سعر اللتر: {obj.petrol_price_per_liter} × 4.5)"

    @admin.display(description='سعر جالون الجازولين (جنيه)')
    def diesel_price_per_gallon_display(self, obj):
        if not obj or not obj.diesel_price_per_liter:
            return "0.00 جنيه"
        return f"{obj.diesel_price_per_gallon} جنيه (سعر اللتر: {obj.diesel_price_per_liter} × 4.5)"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:statement_id>/generate-items/',
                self.admin_site.admin_view(self.generate_items_view),
                name='fleet_fuelmonthlystatement_generate_items',
            ),
            path(
                '<int:statement_id>/print-report/',
                self.admin_site.admin_view(self.print_report_view),
                name='fleet_fuelmonthlystatement_print_report',
            ),
            path(
                '<int:statement_id>/export-csv/',
                self.admin_site.admin_view(self.export_statement_csv_view),
                name='fleet_fuelmonthlystatement_export_csv',
            ),
        ]
        return custom_urls + urls

    def export_statement_csv_view(self, request, statement_id):
        statement = get_object_or_404(models.FuelMonthlyStatement, pk=statement_id)
        return export_statement_items_as_csv(statement)

    def generate_items_view(self, request, statement_id):
       
        statement = get_object_or_404(models.FuelMonthlyStatement, pk=statement_id)
        active_settings = models.FuelBeneficiarySetting.objects.filter(
            is_active_for_fuel=True
        ).select_related('employee')

        has_prices = (statement.petrol_price_per_liter > 0 or statement.diesel_price_per_liter > 0)

        created_count = 0
        updated_count = 0

        for setting in active_settings:
            calculated_amount = statement.calculate_amount(
                setting.default_petrol_liters,
                setting.default_diesel_liters
            ) if has_prices else 0

            item, created = models.FuelDistributionItem.objects.update_or_create(
                statement=statement,
                beneficiary_name=setting.beneficiary_name,
                defaults={
                    'employee': setting.employee,
                    'is_external': setting.is_external,
                    'card_number': setting.card_number,
                    'email': setting.email,
                    'department': setting.department,
                    'job_title': setting.job_title,
                    'petrol_liters': setting.default_petrol_liters,
                    'diesel_liters': setting.default_diesel_liters,
                    'amount': calculated_amount,
                    'created_by': request.user,
                    'updated_by': request.user,
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        if has_prices:
            for item in statement.items.all():
                calc_amount = statement.calculate_amount(item.petrol_liters, item.diesel_liters)
                item.amount = calc_amount
                item.save(update_fields=['amount'])

        price_note = ''
        if has_prices:
            price_note = f" (تم حساب المبالغ بسعر بنزين: {statement.petrol_price_per_liter} جنيه/لتر، جازولين: {statement.diesel_price_per_liter} جنيه/لتر)"

        self.message_user(
            request,
            f" تم توليد وتحديث بنود الكشف ومبالغ الموظفين بنجاح: إضافة {created_count} جديد، وتحديث {updated_count} مستفيد.{price_note}",
            messages.SUCCESS
        )
        return redirect(f'../../{statement_id}/change/')

    def print_report_view(self, request, statement_id):
        """عرض صفحة طباعة تقرير الكشف الشهري بطريقة رسمية ومنسقة"""
        from django.shortcuts import render
        statement = get_object_or_404(models.FuelMonthlyStatement, pk=statement_id)
        items = statement.items.select_related('employee').all()

        context = {
            'statement': statement,
            'items': items,
            'total_petrol': statement.total_petrol_liters,
            'total_diesel': statement.total_diesel_liters,
            'total_amount': statement.total_amount,
        }
        return render(request, 'admin/fleet/fuelmonthlystatement/print_report.html', context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        from django.urls import reverse
        extra_context = extra_context or {}
        extra_context['generate_url'] = reverse(
            'admin:fleet_fuelmonthlystatement_generate_items',
            args=[object_id]
        )
        extra_context['print_report_url'] = reverse(
            'admin:fleet_fuelmonthlystatement_print_report',
            args=[object_id]
        )
        extra_context['export_csv_url'] = reverse(
            'admin:fleet_fuelmonthlystatement_export_csv',
            args=[object_id]
        )
        extra_context['generate_active_count'] = models.FuelBeneficiarySetting.objects.filter(is_active_for_fuel=True).count()
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


    @admin.display(description='توليد بنود الكشف')
    def generate_btn(self, obj):
        from django.urls import reverse
        url = reverse('admin:fleet_fuelmonthlystatement_generate_items', args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" style="background:#f59e0b;color:#fff;padding:4px 12px;border-radius:6px;font-weight:bold;text-decoration:none;white-space:nowrap;" '
            'onclick="return confirm(\'توليد بنود الكشف من الموظفين المفعلين؟\')">'
            'توليد الموظفين</a>',
            url
        )

    @admin.display(description='طباعة تقرير الكشف')
    def print_btn(self, obj):
        from django.urls import reverse
        url = reverse('admin:fleet_fuelmonthlystatement_print_report', args=[obj.pk])
        return format_html(
            '<a href="{}" target="_blank" class="button" style="background:#2563eb;color:#fff;padding:4px 12px;border-radius:6px;font-weight:bold;text-decoration:none;white-space:nowrap;">'
            'طباعة التقرير</a>',
            url
        )


def export_beneficiaries_as_csv(queryset, filename="fuel_beneficiaries.csv"):
    """تصدير مستفيدي الوقود لملف CSV/إكسل مع دعم اللغة العربية بترميز UTF-8 BOM"""
    import csv, codecs
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response)

    writer.writerow([
        'اسم المستفيد',
        'كود الموظف (HR)',
        'رقم بطاقة الوقود',
        'البريد الإلكتروني',
        'الإدارة / القسم',
        'الوظيفة',
        'حصة البنزين (جالون)',
        'حصة الجازولين (جالون)',
        'مفعل للحصول على الوقود',
        'مستفيد خارجي'
    ])

    for obj in queryset:
        emp_code = str(obj.employee.code) if obj.employee and hasattr(obj.employee, 'code') else ''
        writer.writerow([
            obj.beneficiary_name or '',
            emp_code,
            obj.card_number or '',
            obj.email or '',
            obj.department or '',
            obj.job_title or '',
            obj.default_petrol_liters or 0,
            obj.default_diesel_liters or 0,
            'نعم' if obj.is_active_for_fuel else 'لا',
            'نعم' if obj.is_external else 'لا',
        ])

    return response


def export_statement_items_as_csv(statement):
    """تصدير بنود كشف شهري إلى ملف CSV/إكسل"""
    import csv, codecs
    from django.http import HttpResponse

    filename = f"fuel_statement_{statement.id}_{statement.month}_{statement.year}.csv"
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response)

    writer.writerow([
        '#',
        'اسم المستفيد',
        'كود الموظف (HR)',
        'رقم بطاقة الوقود',
        'الوظيفة',
        'الإدارة',
        'حصة البنزين (جالون)',
        'حصة الجازولين (جالون)',
        'إجمالي المبلغ (جنيه)',
        'ملاحظات / التوقيع'
    ])

    items = statement.items.select_related('employee').all()
    for idx, item in enumerate(items, 1):
        emp_code = str(item.employee.code) if item.employee and hasattr(item.employee, 'code') else ''
        writer.writerow([
            idx,
            item.beneficiary_name or '',
            emp_code,
            item.card_number or '',
            item.job_title or '',
            item.department or '',
            item.petrol_liters or 0,
            item.diesel_liters or 0,
            item.amount or 0,
            item.notes_signature or ''
        ])

    return response


def parse_beneficiaries_file(file_obj):
    import csv, zipfile
    import xml.etree.ElementTree as ET

    file_name = file_obj.name.lower()
    rows = []

    if file_name.endswith('.xlsx'):
        try:
            with zipfile.ZipFile(file_obj) as z:
                strings = []
                if 'xl/sharedStrings.xml' in z.namelist():
                    with z.open('xl/sharedStrings.xml') as f:
                        tree = ET.parse(f)
                        for elem in tree.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                            texts = [t.text for t in elem.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if t.text]
                            strings.append(''.join(texts))

                sheets = [name for name in z.namelist() if name.startswith('xl/worksheets/')]
                if sheets:
                    with z.open(sheets[0]) as f:
                        tree = ET.parse(f)
                        ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                        for r in tree.findall('.//s:row', ns):
                            row_cells = []
                            for c in r.findall('s:c', ns):
                                val_type = c.get('t')
                                val_elem = c.find('s:v', ns)
                                val = val_elem.text if val_elem is not None else ''
                                if val_type == 's' and val.isdigit() and int(val) < len(strings):
                                    val = strings[int(val)]
                                row_cells.append(val.strip())
                            if any(row_cells):
                                rows.append(row_cells)
        except Exception:
            pass

    if not rows:
        file_obj.seek(0)
        raw_bytes = file_obj.read()
        for encoding in ['utf-8-sig', 'utf-8', 'cp1256', 'latin-1']:
            try:
                decoded_str = raw_bytes.decode(encoding)
                reader = csv.reader(decoded_str.splitlines())
                rows = [[cell.strip() for cell in row] for row in reader if any(row)]
                if rows:
                    break
            except Exception:
                continue

    return rows


@admin.register(models.FuelDistributionItem)
class FuelDistributionItemAdmin(LogMixin):
    list_display = ('beneficiary_name', 'card_number', 'is_external', 'statement', 'department', 'job_title', 'petrol_liters', 'diesel_liters', 'amount')
    list_filter = ('is_external', 'statement__year', 'statement__month')
    search_fields = ('beneficiary_name', 'card_number', 'email', 'department', 'job_title')
    autocomplete_fields = ('employee',)

    def save_model(self, request, obj, form, change):
        if obj.employee:
            if not obj.beneficiary_name or 'employee' in form.changed_data:
                obj.beneficiary_name = obj.employee.name
            if not obj.card_number or 'employee' in form.changed_data:
                obj.card_number = str(obj.employee.code)
            if not obj.email or 'employee' in form.changed_data:
                obj.email = obj.employee.email or ''
            if not obj.job_title or 'employee' in form.changed_data:
                obj.job_title = obj.employee.mosama_wazifi.name if obj.employee.mosama_wazifi else ''
            if not obj.department or 'employee' in form.changed_data:
                obj.department = obj.employee.hikal_wazifi.name if obj.employee.hikal_wazifi else ''
        super().save_model(request, obj, form, change)


# ─── Restrict HR module/profile access for fleet-only users ───────────────────
from hr.admin import EmployeeBasicAdmin

_orig_has_module_perm = EmployeeBasicAdmin.has_module_permission
_orig_has_view_perm = EmployeeBasicAdmin.has_view_permission
_orig_has_change_perm = EmployeeBasicAdmin.has_change_permission

def _fleet_has_module_permission(self, request):
    if request.user.is_superuser:
        return _orig_has_module_perm(self, request)
    if request.user.groups.filter(name__in=['fleet_manager', 'fleet_employee']).exists() and not request.user.groups.filter(name__in=['hr_manager', 'hr_employee', 'مدير الموارد البشرية', 'موظف الموارد البشرية']).exists():
        return False
    return _orig_has_module_perm(self, request)

def _fleet_has_view_permission(self, request, obj=None):
    if request.user.is_superuser:
        return _orig_has_view_perm(self, request, obj)
    if request.user.groups.filter(name__in=['fleet_manager', 'fleet_employee']).exists() and not request.user.groups.filter(name__in=['hr_manager', 'hr_employee', 'مدير الموارد البشرية', 'موظف الموارد البشرية']).exists():
        if 'autocomplete' in request.path:
            return True
        return False
    return _orig_has_view_perm(self, request, obj)

def _fleet_has_change_permission(self, request, obj=None):
    if request.user.is_superuser:
        return _orig_has_change_perm(self, request, obj)
    if request.user.groups.filter(name__in=['fleet_manager', 'fleet_employee']).exists() and not request.user.groups.filter(name__in=['hr_manager', 'hr_employee', 'مدير الموارد البشرية', 'موظف الموارد البشرية']).exists():
        return False
    return _orig_has_change_perm(self, request, obj)

EmployeeBasicAdmin.has_module_permission = _fleet_has_module_permission
EmployeeBasicAdmin.has_view_permission = _fleet_has_view_permission
EmployeeBasicAdmin.has_change_permission = _fleet_has_change_permission


@admin.register(models.FuelBeneficiarySetting)

class FuelBeneficiarySettingAdmin(LogMixin):
    list_display = ('beneficiary_name', 'card_number', 'is_active_for_fuel', 'is_external', 'default_petrol_liters', 'default_diesel_liters')
    fields = ('employee', 'is_external', 'beneficiary_name', 'card_number', 'default_petrol_liters', 'default_diesel_liters', 'is_active_for_fuel')
    list_filter = ('is_active_for_fuel', 'is_external')
    search_fields = ('beneficiary_name', 'card_number', 'email', 'department', 'job_title')
    list_editable = ('is_active_for_fuel', 'default_petrol_liters', 'default_diesel_liters')
    autocomplete_fields = ('employee',)
    change_list_template = 'admin/fleet/fuelbeneficiarysetting/change_list.html'
    actions = ['export_selected_beneficiaries_action']


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'employee':
            w = formfield.widget
            if hasattr(w, 'can_view_related'):
                w.can_view_related = False
                w.can_change_related = False
                w.can_add_related = False
                w.can_delete_related = False
        return formfield

    def get_form(self, request, obj=None, **kwargs):
        FormClass = super().get_form(request, obj, **kwargs)
        if 'employee' in FormClass.base_fields:
            w = FormClass.base_fields['employee'].widget
            if hasattr(w, 'can_view_related'):
                w.can_view_related = False
                w.can_change_related = False
                w.can_add_related = False
                w.can_delete_related = False
        return FormClass



    @admin.action(description=' تصدير مستفيدي الوقود المختارين إلى CSV/إكسل')
    def export_selected_beneficiaries_action(self, request, queryset):
        return export_beneficiaries_as_csv(queryset, "selected_fuel_beneficiaries.csv")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-csv/', self.admin_site.admin_view(self.export_all_beneficiaries_csv_view), name='fleet_fuelbeneficiarysetting_export_csv'),
            path('import-csv/', self.admin_site.admin_view(self.import_beneficiaries_csv_view), name='fleet_fuelbeneficiarysetting_import_csv'),
        ]
        return custom_urls + urls

    def export_all_beneficiaries_csv_view(self, request):

        queryset = self.get_queryset(request)
        return export_beneficiaries_as_csv(queryset, "all_fuel_beneficiaries.csv")

    def import_beneficiaries_csv_view(self, request):
        if not request.user.is_superuser:
            self.message_user(request, "عذراً، خاصية استيراد ملفات الإكسل متاحة فقط لمدير النظام (Superuser).", messages.ERROR)
            return redirect('../')

        from django.shortcuts import render

        from hr.models import EmployeeBasic

        if request.method == 'POST' and request.FILES.get('import_file'):
            uploaded_file = request.FILES['import_file']
            rows = parse_beneficiaries_file(uploaded_file)

            created_count = 0
            updated_count = 0

            for row in rows:
                if not row or len(row) == 0:
                    continue

                first_cell = str(row[0]).strip().lower()
                if 'اسم' in first_cell or 'name' in first_cell or 'beneficiary' in first_cell:
                    continue

                beneficiary_name = row[0].strip() if len(row) > 0 else ''
                emp_code_val = row[1].strip() if len(row) > 1 else ''
                card_number = row[2].strip() if len(row) > 2 else ''
                email = row[3].strip() if len(row) > 3 else ''
                department = row[4].strip() if len(row) > 4 else ''
                job_title = row[5].strip() if len(row) > 5 else ''

                try:
                    petrol = float(row[6].strip()) if len(row) > 6 and row[6].strip() else 0.0
                except ValueError:
                    petrol = 0.0

                try:
                    diesel = float(row[7].strip()) if len(row) > 7 and row[7].strip() else 0.0
                except ValueError:
                    diesel = 0.0

                is_active = True
                if len(row) > 8 and row[8].strip():
                    val = row[8].strip().lower()
                    if val in ['0', 'false', 'لا', 'no', '0.0']:
                        is_active = False

                if not beneficiary_name and not emp_code_val:
                    continue

                employee_obj = None
                if emp_code_val and emp_code_val.isdigit():
                    employee_obj = EmployeeBasic.objects.filter(code=int(emp_code_val)).first()

                if employee_obj:
                    beneficiary_name = beneficiary_name or employee_obj.name
                    email = email or (employee_obj.email or '')
                    job_title = job_title or (employee_obj.mosama_wazifi.name if employee_obj.mosama_wazifi else '')
                    department = department or (employee_obj.hikal_wazifi.name if employee_obj.hikal_wazifi else '')
                    card_number = card_number or str(employee_obj.code)

                setting = models.FuelBeneficiarySetting.objects.filter(beneficiary_name=beneficiary_name).first()
                created = False
                if not setting:
                    setting = models.FuelBeneficiarySetting(
                        beneficiary_name=beneficiary_name,
                        created_by=request.user
                    )
                    created = True

                setting.employee = employee_obj
                setting.is_external = (employee_obj is None)
                setting.card_number = card_number
                setting.email = email
                setting.department = department
                setting.job_title = job_title
                setting.default_petrol_liters = petrol
                setting.default_diesel_liters = diesel
                setting.is_active_for_fuel = is_active
                setting.updated_by = request.user
                setting.save()

                if created:
                    created_count += 1
                else:
                    updated_count += 1


            self.message_user(
                request,
                f" تم استيراد مستفيدي الوقود بنجاح: إضافة {created_count} مستفيد جديد، وتحديث {updated_count} مستفيد.",
                messages.SUCCESS
            )
            return redirect('../')

        return render(request, 'admin/fleet/fuelbeneficiarysetting/import_excel.html')

    def save_model(self, request, obj, form, change):
        if obj.employee:
            if not obj.beneficiary_name or 'employee' in form.changed_data:
                obj.beneficiary_name = obj.employee.name
            if not obj.card_number or 'employee' in form.changed_data:
                obj.card_number = str(obj.employee.code)
            if not obj.email or 'employee' in form.changed_data:
                obj.email = obj.employee.email or ''
            if not obj.job_title or 'employee' in form.changed_data:
                obj.job_title = obj.employee.mosama_wazifi.name if obj.employee.mosama_wazifi else ''
            if not obj.department or 'employee' in form.changed_data:
                obj.department = obj.employee.hikal_wazifi.name if obj.employee.hikal_wazifi else ''
        super().save_model(request, obj, form, change)






