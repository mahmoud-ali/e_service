from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html
from django.db import models
from django.forms.widgets import TextInput

from gold_travel.forms import TblStateRepresentativeForm
from gold_travel.models import AppPrepareGold, LkpStateDetails, TblStateRepresentative,AppMoveGold, AppMoveGoldDetails

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
            return super().has_change_permission(request,obj)
        
        return False

    def has_delete_permission(self, request, obj=None):
        if not obj or obj.state==1:
            return super().has_delete_permission(request,obj)
        
        return False

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

class LkpStateDetailsAdmin(admin.ModelAdmin):
    model = LkpStateDetails
    list_display = ["state","code","next_serial_no","has_2lestikhbarat_2l3askria"]
    list_filter = ["state","has_2lestikhbarat_2l3askria"]

admin.site.register(LkpStateDetails, LkpStateDetailsAdmin)

class TblStateRepresentativeAdmin(admin.ModelAdmin):
    model = TblStateRepresentative
    form = TblStateRepresentativeForm
    list_display = ["name","state","authority","user"]        
    list_filter = ["authority",("state",admin.RelatedOnlyFieldListFilter)]
    view_on_site = False
            
admin.site.register(TblStateRepresentative, TblStateRepresentativeAdmin)

class AppMoveGoldDetailInline(admin.TabularInline):
    model = AppMoveGoldDetails
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

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
                'fields': [("repr_name","repr_phone"),"repr_address",("repr_identity_type","repr_identity","repr_identity_issue_date")]
            },
        ),
        # (
        #     _("gold data"),
        #     {
        #         'fields': [("gold_weight_in_gram","gold_alloy_count"),"gold_description"]
        #     },
        # ),
        (
            _("attachments"),
            {
                'fields': ["attachement_file"]
            },
        ),
    ]
    list_filter = ["date","state",("source_state",admin.RelatedOnlyFieldListFilter)]
    search_fields = ["code","owner_name","owner_address","repr_name","repr_phone","repr_identity"]
    actions = ['confirm_app']

    view_on_site = False

    def get_list_display(self,request):
        list_display = ["code","date","owner_name","repr_name","gold_weight_in_gram","gold_alloy_count","state","source_state"]
        try:
            authority = request.user.state_representative.authority
            if authority == TblStateRepresentative.AUTHORITY_SMRC:
                return  list_display + ["show_certificate_link"]   
        except:
            pass

        return list_display

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser or request.user.groups.filter(name="gold_travel_manager").exists():
            return qs

        try:
            state_representative = request.user.state_representative
            if state_representative.authority!=TblStateRepresentative.AUTHORITY_SMRC:
                qs = qs.filter(state=(state_representative.authority-1),source_state=state_representative.state)
            else:
                qs = qs.filter(source_state=state_representative.state)
        except:
            qs = qs.none()

        return qs

    def save_model(self, request, obj, form, change):
        try:
            state_representative = request.user.state_representative
            obj.source_state = state_representative.state
            if not obj.code:
                serial_no = state_representative.state.state_gold_travel.next_serial_no
                state_code = state_representative.state.state_gold_travel.code
                obj.code = f"{state_code}/{serial_no:03d}"
                state_representative.state.state_gold_travel.next_serial_no = serial_no+1
                state_representative.state.state_gold_travel.save()
        except Exception as e:
            pass

        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

    def get_actions(self, request):
        actions = super().get_actions(request)
        try:
            authority = request.user.state_representative.authority
            if authority!=TblStateRepresentative.AUTHORITY_SMRC:
                if "confirm_app" in actions:
                    del actions['confirm_app']
        except:
            if "confirm_app" in actions:
                del actions['confirm_app']

        return actions
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

    @admin.display(description=_('gold_weight_in_gram'))
    def gold_weight_in_gram(self, obj):
        return obj.gold_weight_in_gram

    @admin.display(description=_('gold_alloy_count'))
    def gold_alloy_count(self, obj):
        return obj.gold_alloy_count

    @admin.display(description=_('Show certificate'))
    def show_certificate_link(self, obj):
        url = reverse('gold_travel:gold_travel_cert')
        return format_html('<a target="_blank" class="viewlink" href="{url}?id={id}">'+_('Show certificate')+'</a>',
                    url=url,id=obj.id
                )

admin.site.register(AppMoveGold, AppMoveGoldAdmin)

class AppPrepareGoldAdmin(LogAdminMixin,admin.ModelAdmin):
    model = AppPrepareGold
    fields = ["date","owner_name","gold_weight_in_gram","state"] 
    list_filter = ["date","state",("source_state",admin.RelatedOnlyFieldListFilter)]
    search_fields = ["owner_name"]
    view_on_site = False
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    def get_list_display(self,request):
        list_display = ["date","owner_name","gold_weight_in_gram","state","source_state"]  
        try:
            authority = request.user.state_representative.authority
            if authority == TblStateRepresentative.AUTHORITY_SMRC:
                return  list_display + ["show_certificate_link"]   
        except:
            pass

        return list_display

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser or request.user.groups.filter(name="gold_travel_manager").exists():
            return qs

        try:
            state_representative = request.user.state_representative
            qs = qs.filter(source_state=state_representative.state)
        except:
            qs = qs.none()

        return qs

    def save_model(self, request, obj, form, change):
        try:
            state_representative = request.user.state_representative
            obj.issuer = state_representative
            obj.source_state = state_representative.state
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
