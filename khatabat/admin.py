from django.contrib import admin
from django.contrib.auth import get_user_model

from khatabat.forms import KhatabatAdminForm
from .models import Khatabat, HarkatKhatabat, MaktabTanfizi, MaktabTanfiziJiha

User = get_user_model()

class LogMixin:
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:  # New inline object
                instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()
        formset.save_m2m()

class MaktabTanfiziJihaInline(admin.StackedInline):  # You can use StackedInline if you prefer vertical layout
    model = MaktabTanfiziJiha
    min_num = 1  # Minimum number of empty forms
    extra = 0  # Number of empty forms to display

@admin.register(MaktabTanfizi)
class MaktabTanfiziAdmin(admin.ModelAdmin):
    inlines = [MaktabTanfiziJihaInline]
    list_display = ('name',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(groups__name='Maktab Tanfizi')
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class HarkatKhatabatInline(admin.StackedInline):  # You can use StackedInline if you prefer vertical layout
    model = HarkatKhatabat
    min_num = 1  # Minimum number of empty forms
    extra = 0  # Number of empty forms to display
    show_change_link = True


@admin.register(Khatabat)
class KhatabatAdmin(LogMixin,admin.ModelAdmin):
    list_display = ('letter_number', 'subject')
    search_fields = ('letter_number', 'subject')
    inlines = [HarkatKhatabatInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            maktab = request.user.maktab_tanfizi_user

            qs = qs.filter(maktab_tanfizi=maktab)
        except:
            qs = qs.none()
            
        return qs

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if isinstance(inline,HarkatKhatabatInline):
                formset.form = KhatabatAdminForm
                formset.form.request = request

            yield formset,inline
