from django.db import models
from django.shortcuts import redirect
from django.urls import path, reverse

from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.contrib import admin
from django.forms.widgets import TextInput

from company_profile.models import LkpState
from gold_travel_traditional.forms import AppMoveGoldTraditionalRenewForm, AppMoveGoldTraditionalSoldForm
from gold_travel_traditional.models import AppMoveGoldTraditional, GoldTravelTraditionalUserDetail, LkpJihatAlaisdar, LkpSoag

DEFAULT_STATE = LkpState.objects.get(pk=1)

class LkpSoagAdmin(admin.ModelAdmin):
    model = LkpSoag
    list_display = ["state","name"]
    list_filter = ["state"]
    search_fields = ["name"]

admin.site.register(LkpSoag, LkpSoagAdmin)

class LkpJihatAlaisdarAdmin(admin.ModelAdmin):
    model = LkpJihatAlaisdar
    list_display = ["state","name"]
    list_filter = ["state"]
    search_fields = ["name"]

admin.site.register(LkpJihatAlaisdar, LkpJihatAlaisdarAdmin)

class GoldTravelTraditionalUserDetailInline(admin.TabularInline):
    model = GoldTravelTraditionalUserDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class GoldTravelTraditionalUser(admin.ModelAdmin):
    model = AppMoveGoldTraditional
    inlines = [GoldTravelTraditionalUserDetailInline]     

    fields = ["user","name","state"]

class LogAdminMixin:
    def has_add_permission(self, request):
        try:
            request.user.gold_travel_traditional
            return True
        except:
            pass
        
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        try:
            request.user.gold_travel_traditional
            return True
        except:
            pass
        
        return super().has_change_permission(request,obj)

    def has_delete_permission(self, request, obj=None):
        try:
            request.user.gold_travel_traditional
            return True
        except:
            pass
     
        return super().has_delete_permission(request,obj)

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        return super().save_model(request, obj, form, change)                

class AppMoveGoldTraditionalAdmin(LogAdminMixin,admin.ModelAdmin):
    model = AppMoveGoldTraditional

    fieldsets = [
        (
            None,
            {
                'fields': [("code","issue_date"),"gold_weight_in_gram"]
            },
        ),
        (
            _("almustafid data"),
            {
                'fields': [("almustafid_name","almustafid_phone")]
            },
        ),
        (
            _("others"),
            {
                'fields': [("jihat_alaisdar","wijhat_altarhil",),"muharir_alaistimara"]
            },
        ),
    ]

    list_display = ["code","issue_date","gold_weight_in_gram","almustafid_name","almustafid_phone","jihat_alaisdar","wijhat_altarhil","almushtari_name","source_state","state","show_actions"]
    list_filter = ["issue_date",("state",admin.ChoicesFieldListFilter),("source_state",admin.RelatedFieldListFilter),("jihat_alaisdar",admin.RelatedFieldListFilter),("wijhat_altarhil",admin.RelatedFieldListFilter)]
    search_fields = ["code","muharir_alaistimara","almustafid_name","almustafid_phone","almushtari_name"]
    # actions = ['confirm_app','arrived_to_ssmo_app','waived_app','cancel_app','return_to_draft','export_as_csv']
    autocomplete_fields = ["jihat_alaisdar","wijhat_altarhil"]
    # list_editable = ['owner_name_lst']
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    view_on_site = False

    def save_model(self, request, obj, form, change):
        obj.source_state = DEFAULT_STATE

        return super().save_model(request, obj, form, change)                

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("<int:pk>/sold/", self.admin_site.admin_view(self.sold_view)),
            path("<int:pk>/renew/", self.admin_site.admin_view(self.renew_view)),
        ]
        return my_urls + urls
    
    def sold_view(self, request, pk):
        obj = AppMoveGoldTraditional.objects.get(pk=pk)

        if request.method == "POST":
            my_form = AppMoveGoldTraditionalSoldForm(request.POST,instance=obj)
            if my_form.is_valid():
                my_form.save()
                self.message_user(request,_('application changed successfully!'))

            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
        else:
            my_form = AppMoveGoldTraditionalSoldForm(instance=obj)


        context = dict(
            self.admin_site.each_context(request),
            object=obj,
            form=my_form,
            opts=AppMoveGoldTraditional._meta,
            title=_("almushtari_data"),
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/appmovegoldtraditional/sold_application.html", context)

    def renew_view(self, request, pk):
        obj = AppMoveGoldTraditional.objects.get(pk=pk)
        obj_dict = obj.__dict__
        obj_dict['id'] = None
        obj_dict['code'] = ''
        print("dict",obj_dict)

        if request.method == "POST":
            my_form = AppMoveGoldTraditionalRenewForm(request.POST)
            new_obj = my_form.save(commit=False)
            new_obj.state = AppMoveGoldTraditional.STATE_RENEW
            new_obj.created_by = new_obj.updated_by = request.user
            new_obj.source_state = DEFAULT_STATE

            if my_form.is_valid():
                my_form.save()
                self.message_user(request,_('application changed successfully!'))

            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
        else:
            my_form = AppMoveGoldTraditionalRenewForm(initial=obj_dict)


        context = dict(
            self.admin_site.each_context(request),
            object=obj,
            form=my_form,
            opts=AppMoveGoldTraditional._meta,
            title=_("renew_data"),
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/appmovegoldtraditional/sold_application.html", context)

    @admin.display(description=_('show_actions'))
    def show_actions(self, obj):
        url = 'url'
        return format_html('''
                           <ul class="object-tools-actions">
                                <li>
                                    <a class="changelink" href="{id}/sold">{action1} </a>
                                </li>
                                <li>
                                    <a class="changelink" href="{id}/renew">{action2} </a>
                                </li>
                            </ul>
                            ''',
                           id=obj.pk,action1=_('state_sold'),action2=_('state_renew')) #,state1=AppMoveGoldTraditional.STATE_SOLD,action2=_('state_renew'),state2=AppMoveGoldTraditional.STATE_RENEW

admin.site.register(AppMoveGoldTraditional, AppMoveGoldTraditionalAdmin)
