from datetime import date,datetime

from django.contrib import admin
from django.contrib.auth import get_user_model

from django.http import HttpResponse
from django.template.loader import render_to_string

from khatabat.forms import KhatabatAdminForm
from .models import Khatabat, HarkatKhatabat, MaktabTanfizi, MaktabTanfiziJiha

User = get_user_model()

class LogMixin:
    def save_model(self, request, obj, form, change):
        try:
            maktab = request.user.maktab_tanfizi_user
            obj.maktab_tanfizi=maktab
        except:
            pass

        if not change:  # New object
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
        try:
            maktab = request.user.maktab_tanfizi_user

            qs = qs.filter(maktab_tanfizi=maktab)
        except:
            qs = qs.none()

        return qs

    def has_add_permission(self, request):
        try:
            maktab = request.user.maktab_tanfizi_user
            return super().has_add_permission(request)
        except:
            pass

        return False

    def has_change_permission(self, request, obj=None):
        try:
            maktab = request.user.maktab_tanfizi_user
            return super().has_change_permission(request,obj)
        except:
            pass

        return False
    
    def has_delete_permission(self, request, obj=None):
        try:
            maktab = request.user.maktab_tanfizi_user
            return super().has_delete_permission(request,obj)
        except:
            pass

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
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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

class HarkatKhatabatInline(admin.StackedInline):
    model = HarkatKhatabat
    min_num = 1
    extra = 0
    show_change_link = True

@admin.register(Khatabat)
class KhatabatAdmin(MaktabTanfiziMixin,LogMixin,admin.ModelAdmin):
    exclude = ('maktab_tanfizi','created_by', 'updated_by')
    list_display = ('letter_number', 'subject',)
    search_fields = ('letter_number', 'subject')
    inlines = [HarkatKhatabatInline]
    fields =  ('letter_number','subject', )
    # readonly_fields = ['letter_number',]

    def get_changeform_initial_data(self, request):
        maktab_tanfizi = request.user.maktab_tanfizi_user
        last_letter = Khatabat.objects.filter(maktab_tanfizi=maktab_tanfizi).order_by("-created_at").first()
        last_letter_num = int(last_letter.letter_number.split("-")[-1])
        num = f"{maktab_tanfizi.code}-{datetime.now().strftime("%m")}-{last_letter_num+1}"

        return {'letter_number': num}
    
    def get_formsets_with_inlines(self, request, obj=None):
        maktab = request.user.maktab_tanfizi_user

        jiha_all_qs = MaktabTanfiziJiha.objects.filter(maktab_tanfizi=maktab)

        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)            
            if isinstance(inline,HarkatKhatabatInline):
                formset.form = KhatabatAdminForm
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
    list_display = ('subject', 'letter_number', 'movement_type', 'date', 'source_entity', 'procedure', 'delivery_date', 'followup_result')    
    search_fields = ('letter__letter_number', 'letter__subject','note')
    list_filter = ('movement_type','date', 'source_entity', 'procedure', 'delivery_date', 'followup_result')
    actions = [print_html_table]

    @admin.display(description='رقم الخطاب')
    def letter_number(self, obj):
        return obj.letter.letter_number

    @admin.display(description='موضوع الخطاب')
    def subject(self, obj):
        return obj.letter.subject

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            maktab = request.user.maktab_tanfizi_user

            qs = qs.filter(letter__maktab_tanfizi=maktab)
        except:
            qs = qs.none()

        return qs

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
