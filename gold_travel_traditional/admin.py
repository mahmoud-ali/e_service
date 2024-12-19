import codecs
import csv
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import path, reverse

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.forms.widgets import TextInput

from django.contrib import admin

from company_profile.models import LkpState
from gold_travel_traditional.forms import AppMoveGoldTraditionalAddForm, AppMoveGoldTraditionalRenewForm, AppMoveGoldTraditionalSoldForm, GoldTravelTraditionalUserDetailForm, GoldTravelTraditionalUserForm
from gold_travel_traditional.models import AppMoveGoldTraditional, GoldTravelTraditionalUser, GoldTravelTraditionalUserDetail, LkpJihatAlaisdar, LkpSoag

def get_user_state(request):
    try:
        state = request.user.gold_travel_traditional.state
        return state  
    except:
        pass

    return None

class LogAdminMixin:
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        return super().save_model(request, obj, form, change)                

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
    form = GoldTravelTraditionalUserDetailForm
    extra = 1    

class GoldTravelTraditionalUserAdmin(LogAdminMixin,admin.ModelAdmin):
    form = GoldTravelTraditionalUserForm
    inlines = [GoldTravelTraditionalUserDetailInline]     

    fields = ["user","name","state"]

    def get_readonly_fields(self,request, obj=None):
        if obj:
            return self.fields
        
        return super().get_readonly_fields(request,obj)
    
    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if isinstance(inline,GoldTravelTraditionalUserDetailInline):
                formset.form = GoldTravelTraditionalUserDetailForm
                if obj:
                    formset.form.allowed_state = obj.state
            yield formset,inline

admin.site.register(GoldTravelTraditionalUser, GoldTravelTraditionalUserAdmin)

class AppMoveGoldTraditionalAdmin(LogAdminMixin,admin.ModelAdmin):
    # model = AppMoveGoldTraditional
    form = AppMoveGoldTraditionalAddForm

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
                'fields': [("jihat_alaisdar","wijhat_altarhil",),("muharir_alaistimara","almushtari_name")]
            },
        ),
    ]
    # readonly_fields = ["almushtari_name"]
    list_display = ["code","issue_date","gold_weight_in_gram","almustafid_name","almustafid_phone","jihat_alaisdar","wijhat_altarhil","almushtari_name","source_state","parent_link","state","show_actions"]
    list_filter = ["issue_date",("state",admin.ChoicesFieldListFilter),("source_state",admin.RelatedFieldListFilter),("jihat_alaisdar",admin.RelatedFieldListFilter),("wijhat_altarhil",admin.RelatedFieldListFilter)]
    search_fields = ["code","muharir_alaistimara","almustafid_name","almustafid_phone","almushtari_name"]
    actions = ['export_as_csv']
    autocomplete_fields = ["jihat_alaisdar","wijhat_altarhil"]
    # list_editable = ['owner_name_lst']
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    view_on_site = False
    class Media:
        css = {
        "all": ["gold_travel_traditional/css/all.css"],
        }

        js = ["admin/js/jquery.init.js"]

    def save_model(self, request, obj, form, change):
        obj.source_state = get_user_state(request)

        return super().save_model(request, obj, form, change)                

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser or request.user.groups.filter(name="gold_travel_traditional_manager").exists():
            return qs

        try:
            gold_travel_traditional_user = request.user.gold_travel_traditional
            qs = qs\
                .filter(source_state=gold_travel_traditional_user.state)\
                .filter(wijhat_altarhil__in=gold_travel_traditional_user.goldtraveltraditionaluserdetail_set.values_list('soug',flat=True))
        except:
            qs = qs.none()

        return qs

    def get_form(self, request, obj=None, **kwargs):
        my_form = self.form
        my_form.allowed_state = get_user_state(request)
        kwargs["form"] = my_form
        return super().get_form(request, obj, **kwargs)

    def has_add_permission(self, request):
        try:
            request.user.gold_travel_traditional
            return True
        except:
            pass
        
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        # try:
        #     request.user.gold_travel_traditional
        #     if obj and obj.state in [AppMoveGoldTraditional.STATE_NEW,AppMoveGoldTraditional.STATE_RENEW]:
        #         return True
        #     else:
        #         return False
        # except:
        #     pass

        if obj and obj.state in [AppMoveGoldTraditional.STATE_SOLD,AppMoveGoldTraditional.STATE_CANCLED]:
            return False
        
        return super().has_change_permission(request,obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.state in [AppMoveGoldTraditional.STATE_SOLD,AppMoveGoldTraditional.STATE_CANCLED]:
            return False

        return super().has_delete_permission(request,obj)

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
                if obj and obj.state in [AppMoveGoldTraditional.STATE_NEW,AppMoveGoldTraditional.STATE_RENEW]:
                    new_obj = my_form.save(commit=False)
                    new_obj.state = AppMoveGoldTraditional.STATE_SOLD
                    new_obj.save()
                    self.log_change(request,obj,_('state_sold'))
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

        if request.method == "POST":
            my_form = AppMoveGoldTraditionalRenewForm(request.POST)

            if my_form.is_valid():
                if obj and obj.state in [AppMoveGoldTraditional.STATE_EXPIRED]:
                    obj.state = AppMoveGoldTraditional.STATE_CANCLED
                    obj.save()
                    self.log_change(request,obj,_('state_cancled'))

                    new_obj = my_form.save(commit=False)
                    new_obj.id = new_obj.pk = None
                    new_obj.state = AppMoveGoldTraditional.STATE_RENEW
                    new_obj.created_by = new_obj.updated_by = request.user
                    new_obj.source_state = get_user_state(request)
                    new_obj.parent = obj

                    new_obj.save()
                    self.log_change(request,new_obj,_('state_renew'))
                    self.message_user(request,_('application changed successfully!'))

                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_changelist"
                        % (
                            self.admin_site.name,
                            obj._meta.app_label,
                            obj._meta.model_name,
                        )
                    )
                )
        else:
            obj.code = ''
            obj.issue_date = timezone.now().date()
            my_form = AppMoveGoldTraditionalRenewForm(instance=obj)

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
                    'fields': [("jihat_alaisdar","wijhat_altarhil",),("muharir_alaistimara",)]
                },
            ),
        ]
        # fieldsets = [(None, {"fields": list(my_form.base_fields)})]
        admin_form = admin.helpers.AdminForm(my_form, fieldsets, {})

        context = dict(
            self.admin_site.each_context(request),
            original= obj,
            adminform =admin_form, 
            opts=self.opts,
            title=_("renew_data"),
            has_add_permission=True,
            has_change_permission=True,
            has_delete_permission=False,
            has_view_permission=True,
            has_editable_inline_admin_formsets=False,
            add=False,
            change= True,
            save_as=False,
            show_save=False,
        )
        # return TemplateResponse(request, "admin/gold_travel_traditional/appmovegoldtraditional/renew_application.html", context)
        return TemplateResponse(request, "admin/change_form.html", context)

    @admin.display(description=_('parent'))
    def parent_link(self,obj):
        if obj.parent:
            url = reverse("admin:gold_travel_traditional_appmovegoldtraditional_change", args=(obj.parent.id,))
            return format_html('<a href={url}>{txt}</a>',url=url,txt=obj.parent)
        
        return '-'
    
    @admin.display(description=_('show_actions'))
    def show_actions(self, obj):
        url = 'url'

        def get_allowed_actions(obj):
            if obj.state in [AppMoveGoldTraditional.STATE_NEW,AppMoveGoldTraditional.STATE_RENEW]:
                return format_html('''
                    <ul class="actions-list">
                        <li>
                            <a class="changelink" href="{id}/sold">{action1} </a>
                        </li>
                    </ul>
                ''',id=obj.pk,action1=_('state_sold'))
            
            if obj.state in [AppMoveGoldTraditional.STATE_EXPIRED]:
                return format_html('''
                    <ul class="actions-list">
                        <li>
                            <a class="changelink" href="{id}/renew">{action1} </a>
                        </li>
                    </ul>
                ''',id=obj.pk,action1=_('state_renew'))
            
            return format_html('<ul class="actions-list"><li>&nbsp;</li></ul>')

        return get_allowed_actions(obj)

    @admin.action(description=_('Export data'))
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="move_gold_form.csv"'},
        )
        header = [
                    _("code"),_("issue_date"),_('gold_weight_in_gram'),_("almustafid_name"),_("almustafid_phone"),_( "jihat_alaisdar"),\
                    _("wijhat_altarhil"),_("almushtari_name"),_("muharir_alaistimara"),_("source_state"),_("record_state"),_("parent"),\
                    _("created_at"),_("created_by"),_("updated_at"),_("updated_by")
        ]

        # BOM
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(header)

        for app in queryset:
            parent_code = None
            if hasattr(app,'parent') and app.parent:
                parent_code = app.parent.code

            row = [
                    app.code,app.issue_date,app.gold_weight_in_gram,app.almustafid_name,app.almustafid_phone,app.jihat_alaisdar,\
                    app.wijhat_altarhil,app.almushtari_name,app.muharir_alaistimara,app.source_state,app.get_state_display(),parent_code,\
                    app.created_at,app.created_by,app.updated_at,app.updated_by,
            ]
            writer.writerow(row)

        return response

admin.site.register(AppMoveGoldTraditional, AppMoveGoldTraditionalAdmin)
