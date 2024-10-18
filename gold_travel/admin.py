from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html

from gold_travel.forms import TblStateRepresentativeForm
from gold_travel.models import AppPrepareGold, TblStateRepresentative,AppMoveGold, AppMoveGoldDetails

class LogAdminMixin:
    def has_add_permission(self, request, obj=None):
        try:
            if request.user.state_representative.authority==TblStateRepresentative.AUTHORITY_SMRC:
                return True
        except:
            pass
        
        return False

    def has_change_permission(self, request, obj=None):
        if not obj or obj.state==1:
            return True
        
        return False

    def has_delete_permission(self, request, obj=None):
        if not obj or obj.state==1:
            return True
        
        return False

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

class TblStateRepresentativeAdmin(admin.ModelAdmin):
    model = TblStateRepresentative
    form = TblStateRepresentativeForm
    list_display = ["authority","user","state"]        
    list_filter = ["authority","state"]
    view_on_site = False
            
admin.site.register(TblStateRepresentative, TblStateRepresentativeAdmin)

class AppMoveGoldDetailInline(admin.TabularInline):
    model = AppMoveGoldDetails
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppMoveGoldAdmin(LogAdminMixin,admin.ModelAdmin):
    model = AppMoveGold
    inlines = [AppMoveGoldDetailInline]     

    fieldsets = [
        (
            None,
            {
                'fields': ["date","destination"]
            },
        ),
        (
            _("owner data"),
            {
                'fields': ["owner_name","owner_address"]
            },
        ),
        (
            _("representative data"),
            {
                'fields': [("repr_name","repr_phone"),"repr_address",("repr_identity","repr_identity_issue_date")]
            },
        ),
        (
            _("gold data"),
            {
                'fields': [("gold_weight_in_gram","gold_alloy_count"),"gold_description"]
            },
        ),
        (
            _("attachments"),
            {
                'fields': ["attachement_file"]
            },
        ),
    ]
    list_display = ["date","owner_name","repr_name","gold_weight_in_gram","gold_alloy_count","state"]        
    list_filter = ["date","owner_name"]
    search_fields = ["owner_name","owner_address","repr_name","repr_phone","repr_identity"]
    actions = ['confirm_app']

    view_on_site = False

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser or request.user.groups.filter(name="gold_travel_manager").exists():
            return qs

        try:
            authority = request.user.state_representative.authority
            qs = qs.filter(state=(authority-1))
        except:
            qs = qs.none()

        return qs

    @admin.action(description=_('Confirm application'))
    def confirm_app(self, request, queryset):
        try:
            authority = request.user.state_representative.authority
            change_flag = False
            for obj in queryset:
                if (obj.state+1)==authority:
                    obj.state = authority
                    obj.save()
                    change_flag = True

            if change_flag:
                self.message_user(request,_('application confirmed successfully!'))
        except:
            pass

admin.site.register(AppMoveGold, AppMoveGoldAdmin)

class AppPrepareGoldAdmin(LogAdminMixin,admin.ModelAdmin):
    model = AppPrepareGold
    fields = ["date","owner_name","gold_weight_in_gram","state"] 
    list_filter = ["date","state"]
    view_on_site = False

    def get_list_display(self,request):
        list_display = ["date","owner_name","gold_weight_in_gram","state"]  
        try:
            authority = request.user.state_representative.authority
            if authority == TblStateRepresentative.AUTHORITY_SMRC:
                return  list_display + ["show_certificate_link"]   
        except:
            pass

        return list_display

    def save_model(self, request, obj, form, change):
        try:
            usr = request.user.state_representative
            obj.issuer = usr

        except Exception as e:
            pass

        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

    @admin.display(description=_('Show certificate'))
    def show_certificate_link(self, obj):
        url = reverse('gold_travel:whom_may_concern')
        return format_html('<a target="_blank" class="viewlink" href="{url}?id={id}">'+_('Show certificate')+'</a>',
                    url=url,id=obj.id
                )

admin.site.register(AppPrepareGold, AppPrepareGoldAdmin)
