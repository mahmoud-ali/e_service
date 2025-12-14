from datetime import date,datetime

from django.urls import reverse
from django.utils.html import format_html

from django.contrib import admin
from django.contrib.auth import get_user_model

from django.http import HttpResponse
from django.template.loader import render_to_string

from khatabat.forms import HarkatKhatabatInboxAdminForm,HarkatKhatabatOutboxAdminForm
from .models import HarkatKhatabatInbox, HarkatKhatabatOutbox, Khatabat, HarkatKhatabat, MaktabTanfizi, MaktabTanfiziJiha, Motab3atKhatabat

User = get_user_model()

class LogMixin:
    def save_model(self, request, obj, form, change):
        try:
            maktab = request.user.maktab_tanfizi_user
            obj.maktab_tanfizi=maktab
        except:
            maktab = request.user.maktab_tanfizi_follow_up
            obj.maktab_tanfizi=maktab

        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        for form in formset.forms:
            if form.cleaned_data.get('DELETE', False):
                if form.instance.pk:
                    form.instance.delete()

        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:  # New inline object
                instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()
        formset.save_m2m()

class MaktabTanfiziMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        maktab = None

        if hasattr(request.user,"maktab_tanfizi_user"):
            maktab = request.user.maktab_tanfizi_user
            qs = qs.filter(maktab_tanfizi=maktab)
        elif hasattr(request.user,"maktab_tanfizi_follow_up"):
            maktab = request.user.maktab_tanfizi_follow_up
            qs = qs.filter(maktab_tanfizi=maktab,has_motab3at=True)
        elif hasattr(request.user,"maktab_tanfizi_manager"):
            maktab = request.user.maktab_tanfizi_manager.first()
            qs = qs.filter(maktab_tanfizi=maktab)
        else:
            qs = qs.none()

        return qs

    def has_add_permission(self, request):
        if hasattr(request.user,"maktab_tanfizi_user") or hasattr(request.user,"maktab_tanfizi_follow_up"):
            return super().has_add_permission(request)

        return False

    def has_change_permission(self, request, obj=None):
        if hasattr(request.user,"maktab_tanfizi_user") or hasattr(request.user,"maktab_tanfizi_follow_up"):
            return super().has_change_permission(request,obj)

        return False
    
    def has_delete_permission(self, request, obj=None):
        if hasattr(request.user,"maktab_tanfizi_user") or hasattr(request.user,"maktab_tanfizi_follow_up"):
            return super().has_delete_permission(request,obj)
        
        return False

class MaktabTanfiziJihaInline(admin.StackedInline):
    model = MaktabTanfiziJiha
    min_num = 0  # Minimum number of empty forms
    extra = 0  # Number of empty forms to display

@admin.register(MaktabTanfizi)
class MaktabTanfiziAdmin(admin.ModelAdmin):
    inlines = [MaktabTanfiziJihaInline]
    list_display = ('name',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(groups__name='Maktab Tanfizi')

        if db_field.name == "follow_up":
            kwargs["queryset"] = User.objects.filter(groups__name='Maktab Tanfizi Follow up')
           
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "manager":
            kwargs["queryset"] = User.objects.filter(groups__name='Maktab Tanfizi Manager')
            
        return super().formfield_for_manytomany(db_field, request, **kwargs)

@admin.register(MaktabTanfiziJiha)
class MaktabTanfiziJihaAdmin(MaktabTanfiziMixin, admin.ModelAdmin):
    model = MaktabTanfiziJiha
    exclude = ('maktab_tanfizi',)
    list_display = ('name',)

    def save_model(self, request, obj, form, change):
        try:
            maktab = request.user.maktab_tanfizi_user
            obj.maktab_tanfizi=maktab
        except:
            pass

        super().save_model(request, obj, form, change)

class HarakaMixin:
    min_num = 0
    extra = 0
    show_change_link = True
    classes = ['collapse']

class HarkatKhatabatInboxInline(HarakaMixin,admin.StackedInline):
    model = HarkatKhatabatInbox
    form = HarkatKhatabatInboxAdminForm
class HarkatKhatabatOutboxInline(HarakaMixin,admin.StackedInline):
    model = HarkatKhatabatOutbox
    form = HarkatKhatabatOutboxAdminForm

class Motab3atKhatabatInline(admin.TabularInline):
    model = Motab3atKhatabat
    min_num = 0
    extra = 0
    show_change_link = True
    classes = ["wide", "collapse"]

@admin.register(Khatabat)
class KhatabatAdmin(MaktabTanfiziMixin,LogMixin,admin.ModelAdmin):
    exclude = ('maktab_tanfizi','created_by', 'updated_by')
    list_display = ('letter_number', 'subject','first_haraka')
    list_display_links = ('letter_number', 'subject',)
    search_fields = ('letter_number', 'subject','tags')
    inlines = [HarkatKhatabatInboxInline,HarkatKhatabatOutboxInline,]
    fields =  ('letter_number','subject','has_motab3at','tags' )
    readonly_fields = []

    @admin.display(description='الحركة الابتدائية')
    def first_haraka(self, obj):
        if obj.harkatkhatabat_set.exists():
            haraka_obj = obj.harkatkhatabat_set.first()
            url = reverse("admin:khatabat_harkatkhatabat_change", args=[haraka_obj.id])
            return format_html('<a href="{}">{}</a>', url, haraka_obj.get_movement_type_display())            
            
        
        return '-'

    def get_readonly_fields(self, request, obj=None):
        readonly = super().get_readonly_fields(request, obj)
        if hasattr(request.user,"maktab_tanfizi_user"):
            if obj and obj.motab3atkhatabat_set.exists():
                readonly.append("has_motab3at")

        elif hasattr(request.user,"maktab_tanfizi_follow_up"):
            readonly.append("letter_number")
            readonly.append("subject")
            readonly.append("has_motab3at")

        return readonly
    
    def get_changeform_initial_data(self, request):
        maktab_tanfizi = request.user.maktab_tanfizi_user
        last_letter = Khatabat.objects.filter(maktab_tanfizi=maktab_tanfizi).order_by("-created_at").first()
        last_letter_num = 0
        try:
            last_letter_num = int(last_letter.letter_number.split("-")[-1])
        except:
            pass
        num = f"{maktab_tanfizi.code}-{datetime.now().strftime("%m")}-{last_letter_num+1}"

        return {'letter_number': num}
    
    def get_inlines(self,request, obj):
        my_inlines = super().get_inlines(request, obj)
        if not hasattr(request.user,"maktab_tanfizi_user"):
            if obj:
                inlines = []
                for inline in [HarkatKhatabatInboxInline,HarkatKhatabatOutboxInline,]:
                    related_model = inline.model

                    qs = related_model.objects.filter(letter= obj)

                    if qs.exists():
                        inlines.append(inline)

                my_inlines = inlines

        if obj and (obj.has_motab3at or obj.motab3atkhatabat_set.exists()):
            return my_inlines + [Motab3atKhatabatInline]
        
        return my_inlines
    
    def get_formsets_with_inlines(self, request, obj=None):
        maktab = None

        if hasattr(request.user,"maktab_tanfizi_user"):
            maktab = request.user.maktab_tanfizi_user
        elif hasattr(request.user,"maktab_tanfizi_follow_up"):
            maktab = request.user.maktab_tanfizi_follow_up
        elif hasattr(request.user,"maktab_tanfizi_manager"):
            maktab = request.user.maktab_tanfizi_manager.first()

        jiha_all_qs = MaktabTanfiziJiha.objects.filter(maktab_tanfizi=maktab)

        for inline in self.get_inline_instances(request, obj):
            count = inline.model.objects.filter(letter=obj).count()
            inline.verbose_name_plural = f"{inline.verbose_name_plural} ({count})"

            formset = inline.get_formset(request, obj)            
            if isinstance(inline,HarkatKhatabatInboxInline):
                formset.form.request = request
                formset.form.qs = jiha_all_qs

            if isinstance(inline,HarkatKhatabatOutboxInline):
                formset.form.request = request
                formset.form.qs = jiha_all_qs

            yield formset,inline

@admin.action(description="طباعة فورم تسليم")
def print_html_table(modeladmin, request, queryset):
    qs = queryset #.filter(delivery_date__isnull=True)
    html = render_to_string('khatabat/receive.html', {
        "queryset": qs,
        "date":date.isoformat(date.today())
    })

    # Return as downloadable HTML
    response = HttpResponse(html, content_type="text/html; charset=utf-8")
    # response["Content-Disposition"] = "attachment; filename=report.html"
    return response


@admin.register(HarkatKhatabat)
class HarkatKhatabatAdmin(admin.ModelAdmin):
    model = HarkatKhatabat
    list_display = ('subject', 'letter_number', 'movement_type', 'date', 'procedure', 'delivery_date', 'source_entity','forwarded_to_list')    
    search_fields = ('letter__letter_number', 'letter__subject','note')
    list_filter = ('movement_type','date', 'procedure', 'delivery_date', 'source_entity', 'forwarded_to')
    actions = [print_html_table]

    @admin.display(description='رقم الخطاب')
    def letter_number(self, obj):
        return obj.letter.letter_number

    @admin.display(description='موضوع الخطاب')
    def subject(self, obj):
        return obj.letter.subject

    @admin.display(description="جهة التحويل")
    def forwarded_to_list(self, obj):
        l = list(obj.forwarded_to.values_list('name',flat=True))
        return "، ".join(l)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        maktab = None
        if hasattr(request.user,"maktab_tanfizi_user"):
            maktab = request.user.maktab_tanfizi_user
            qs = qs.filter(letter__maktab_tanfizi=maktab)
        elif hasattr(request.user,"maktab_tanfizi_follow_up"):
            maktab = request.user.maktab_tanfizi_follow_up
            qs = qs.filter(letter__maktab_tanfizi=maktab,letter__has_motab3at=True)
        elif hasattr(request.user,"maktab_tanfizi_manager"):
            maktab = request.user.maktab_tanfizi_manager.first()
            qs = qs.filter(letter__maktab_tanfizi=maktab)
        else:
            qs = qs.none()

        return qs

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Motab3atKhatabat)
class Motab3atKhatabatAdmin(admin.ModelAdmin):
    model = Motab3atKhatabat
    list_display = ('subject', 'letter_number', 'date', 'action', 'done',)    
    search_fields = ('letter__letter_number', 'letter__subject','note')
    list_filter = ('date', 'done',)
    actions = [print_html_table]

    @admin.display(description='رقم الخطاب')
    def letter_number(self, obj):
        return obj.letter.letter_number

    @admin.display(description='موضوع الخطاب')
    def subject(self, obj):
        return obj.letter.subject

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        maktab = None
        if hasattr(request.user,"maktab_tanfizi_follow_up"):
            maktab = request.user.maktab_tanfizi_follow_up
            qs = qs.filter(letter__maktab_tanfizi=maktab,letter__has_motab3at=True)
        elif hasattr(request.user,"maktab_tanfizi_manager"):
            maktab = request.user.maktab_tanfizi_manager.first()
            qs = qs.filter(letter__maktab_tanfizi=maktab)
        else:
            qs = qs.none()

        return qs

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
