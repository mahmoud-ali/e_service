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
from gold_travel_traditional.forms import AppMoveGoldTraditionalAddForm, AppMoveGoldTraditionalRenewForm, AppMoveGoldTraditionalSoldForm, GoldTravelTraditionalUserJihatAlaisdarForm, GoldTravelTraditionalUserJihatTarhilForm, GoldTravelTraditionalUserForm
from gold_travel_traditional.models import AppMoveGoldTraditional, AppMoveGoldTraditionalDetail, GoldTravelTraditionalUser, GoldTravelTraditionalUserJihatAlaisdar, GoldTravelTraditionalUserJihatTarhil, LkpJihatAlaisdar, LkpJihatAltarhil

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

class LkpJihatAltarhilAdmin(admin.ModelAdmin):
    model = LkpJihatAltarhil
    list_display = ["state","name"]
    list_filter = ["state"]
    search_fields = ["name"]

admin.site.register(LkpJihatAltarhil, LkpJihatAltarhilAdmin)

class LkpJihatAlaisdarAdmin(admin.ModelAdmin):
    model = LkpJihatAlaisdar
    list_display = ["state","name"]
    list_filter = ["state"]
    search_fields = ["name"]

admin.site.register(LkpJihatAlaisdar, LkpJihatAlaisdarAdmin)

class GoldTravelTraditionalUserJihatAlaisdarInline(admin.TabularInline):
    model = GoldTravelTraditionalUserJihatAlaisdar
    form = GoldTravelTraditionalUserJihatAlaisdarForm
    extra = 1

class GoldTravelTraditionalUserJihatTarhilInline(admin.TabularInline):
    model = GoldTravelTraditionalUserJihatTarhil
    form = GoldTravelTraditionalUserJihatTarhilForm
    extra = 1

class GoldTravelTraditionalUserAdmin(LogAdminMixin,admin.ModelAdmin):
    form = GoldTravelTraditionalUserForm
    inlines = [GoldTravelTraditionalUserJihatAlaisdarInline, GoldTravelTraditionalUserJihatTarhilInline]     

    fields = ["user","name","state"]

    def get_readonly_fields(self,request, obj=None):
        if obj:
            return self.fields
        
        return super().get_readonly_fields(request,obj)
    
    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if not obj:
                return formset, None

            if isinstance(inline, GoldTravelTraditionalUserJihatAlaisdarInline):
                formset.form = GoldTravelTraditionalUserJihatAlaisdarForm
                if obj:
                    formset.form.allowed_state = obj.state
            elif isinstance(inline, GoldTravelTraditionalUserJihatTarhilInline):
                formset.form = GoldTravelTraditionalUserJihatTarhilForm
                if obj:
                    formset.form.allowed_state = obj.state
            yield formset,inline

admin.site.register(GoldTravelTraditionalUser, GoldTravelTraditionalUserAdmin)

class AppMoveGoldTraditionalDetailInline(admin.TabularInline):
    model = AppMoveGoldTraditionalDetail
    extra = 1

class AppMoveGoldTraditionalAdmin(LogAdminMixin,admin.ModelAdmin):
    # model = AppMoveGoldTraditional
    form = AppMoveGoldTraditionalAddForm
    inlines = [AppMoveGoldTraditionalDetailInline]

    fieldsets = [
        (
            None,
            {
                'fields': ["code","issue_date"]
            },
        ),
        (
            _("almustafid data",),
            {
                'fields': [("almustafid_name","almustafid_phone"), ("almustafid_identity_type", "almustafid_identity","almustafid_identity_attachement")]
            },
        ),
        (
            _("others"),
            {
                'fields': [("jihat_alaisdar","wijhat_altarhil",),("attachement_file",)]
            },
        ),
    ]
    readonly_fields = ["code"]
    # readonly_fields = ["almushtari_name"]
    list_display = ["code","issue_date","total_gold_weight_display","almustafid_name","jihat_alaisdar","wijhat_altarhil","source_state","state","show_actions"]
    list_filter = [("state",admin.ChoicesFieldListFilter),("source_state",admin.RelatedFieldListFilter),("jihat_alaisdar",admin.RelatedFieldListFilter),("wijhat_altarhil",admin.RelatedFieldListFilter)]
    date_hierarchy = "issue_date"
    search_fields = ["code","almustafid_name","almustafid_phone","almushtari_name"]
    actions = ['export_as_csv']
    # autocomplete_fields = ["jihat_alaisdar","wijhat_altarhil"]
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
            
            allowed_alaisdar = gold_travel_traditional_user.goldtraveltraditionaluserjihatalaisdar_set.values_list('jihat_alaisdar', flat=True)
            allowed_tarhil = gold_travel_traditional_user.goldtraveltraditionaluserjihattarhil_set.values_list('wijhat_altarhil', flat=True)
            
            qs = qs.filter(source_state=gold_travel_traditional_user.state)
            qs = qs.filter(
                models.Q(jihat_alaisdar__in=allowed_alaisdar) | 
                models.Q(wijhat_altarhil__in=allowed_tarhil)
            )
        except:
            qs = qs.none()

        return qs

    def get_form(self, request, obj=None, **kwargs):
        my_form = self.form
        my_form.user = request.user
        my_form.allowed_state = get_user_state(request)
        kwargs["form"] = my_form
        return super().get_form(request, obj, **kwargs)

    def has_add_permission(self, request):
        try:
            gold_user = request.user.gold_travel_traditional
            # Check if user has any assigned jihat_alaisdar
            if not gold_user.goldtraveltraditionaluserjihatalaisdar_set.exists():
                return False
            return True
        except:
            pass
        
        return False

    def has_change_permission(self, request, obj=None):            
        if obj:
            if obj.state != AppMoveGoldTraditional.STATE_NEW:
                return False
            
            # Check if user belongs to the jihat_alaisdar of the record
            try:
                gold_user = request.user.gold_travel_traditional
                allowed_alaisdar = gold_user.goldtraveltraditionaluserjihatalaisdar_set.values_list('jihat_alaisdar', flat=True)
                if obj.jihat_alaisdar_id not in allowed_alaisdar:
                    return False
            except:
                return False
        
        return False

    def has_delete_permission(self, request, obj=None):
        if obj:
            if request.user.is_superuser and obj.state == AppMoveGoldTraditional.STATE_NEW:
                return True
        
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("<int:pk>/sold/", self.admin_site.admin_view(self.sold_view)),
            path("<int:pk>/renew/", self.admin_site.admin_view(self.renew_view)),
            path("<int:pk>/arrived/", self.admin_site.admin_view(self.arrived_view)),
            path("<int:pk>/print/", self.admin_site.admin_view(self.print_view)),
        ]
        return my_urls + urls

    def print_view(self, request, pk):
        from gold_travel_traditional.models import AppMoveGoldTraditional
        obj = AppMoveGoldTraditional.objects.get(pk=pk)

        # Permission check: Alaisdar user or superuser
        try:
            gold_user = request.user.gold_travel_traditional
            allowed_alaisdar = gold_user.goldtraveltraditionaluserjihatalaisdar_set.values_list('jihat_alaisdar', flat=True)
            if obj.jihat_alaisdar_id not in allowed_alaisdar:
                self.message_user(request, _('Only users from the issuing location can print this report.'), level='error')
                return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
        except:
            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        # Prepare alloy chunks for the template
        details = list(obj.details.all())
        chunk_size = 40
        alloy_chunks = []
        for i in range(0, len(details), chunk_size):
            chunk = details[i:i + chunk_size]
            half = (len(chunk) + 1) // 2
            left_half = chunk[:half]
            right_half = chunk[half:]
            # Zip them together for the template, padding with None if necessary
            from itertools import zip_longest
            rows = list(zip_longest(left_half, right_half))
            alloy_chunks.append({
                'rows': rows,
                'start_index': i + 1,
                'half_offset': half
            })

        context = {
            'object': obj,
            'alloy_chunks': alloy_chunks,
            'has_astikhbarat': False, 
        }
        return TemplateResponse(request, "gold_travel_traditional/gold_travel_traditional.html", context)
    
    def arrived_view(self, request, pk):
        obj = AppMoveGoldTraditional.objects.get(pk=pk)
        
        # Check if user has permission for this destination
        try:
            gold_user = request.user.gold_travel_traditional
            if obj.wijhat_altarhil not in LkpJihatAltarhil.objects.filter(id__in=gold_user.goldtraveltraditionaluserjihattarhil_set.values_list('wijhat_altarhil', flat=True)):
                 self.message_user(request, _('Only users assigned to the destination location can mark this as arrived.'), level='error')
                 return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
        except:
             return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if obj.state in [AppMoveGoldTraditional.STATE_NEW, AppMoveGoldTraditional.STATE_RENEW, AppMoveGoldTraditional.STATE_EXPIRED]:
            obj.state = AppMoveGoldTraditional.STATE_ARRIVED
            obj.updated_by = request.user
            obj.save()
            self.log_change(request, obj, _('state_arrived'))
            self.message_user(request, _('application marked as arrived successfully!'))
        
        return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
    
    def sold_view(self, request, pk):
        obj = AppMoveGoldTraditional.objects.get(pk=pk)

        if request.method == "POST":
            my_form = AppMoveGoldTraditionalSoldForm(request.POST,instance=obj)
            if my_form.is_valid():
                if obj and obj.state in [AppMoveGoldTraditional.STATE_NEW,AppMoveGoldTraditional.STATE_RENEW, AppMoveGoldTraditional.STATE_EXPIRED, AppMoveGoldTraditional.STATE_ARRIVED]:
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
            my_form.user = request.user

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
            my_form.user = request.user

        fieldsets = [
            (
                None,
                {
                    'fields': [("code","issue_date")]
                },
            ),
            (
                _("almustafid data"),
                {
                    'fields': [("almustafid_name","almustafid_phone"), ("almustafid_identity_type", "almustafid_identity")]
                },
            ),
            (
                _("others"),
                {
                    'fields': [("jihat_alaisdar","wijhat_altarhil",)]
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

    @admin.display(description=_('gold_weight_in_gram'))
    def total_gold_weight_display(self, obj):
        return obj.gold_weight_in_gram

    @admin.display(description=_('parent'))
    def parent_link(self,obj):
        if obj.parent:
            url = reverse("admin:gold_travel_traditional_appmovegoldtraditional_change", args=(obj.parent.id,))
            return format_html('<a href="{url}">{txt}</a>',url=url,txt=obj.parent.code)
        
        return '-'
    
    @admin.display(description=_('show_actions'))
    def show_actions(self, obj):
        request = self.current_request
        is_manager = request.user.groups.filter(name="gold_travel_traditional_manager").exists()

        def get_allowed_actions(obj):
            actions = []
            
            is_alaisdar_user = False
            try:
                gold_user = request.user.gold_travel_traditional
                if obj.jihat_alaisdar_id in gold_user.goldtraveltraditionaluserjihatalaisdar_set.values_list('jihat_alaisdar', flat=True):
                    is_alaisdar_user = True
            except:
                pass

            # Action for Alaisdar users (Sold)
            # if obj.state in [AppMoveGoldTraditional.STATE_NEW, AppMoveGoldTraditional.STATE_RENEW, AppMoveGoldTraditional.STATE_EXPIRED, AppMoveGoldTraditional.STATE_ARRIVED]:
            #     if is_alaisdar_user:
            #         actions.append(f'<li><a class="changelink" href="{obj.pk}/sold">{_("state_sold")}</a></li>')
            
            # Action for Alaisdar users (Renew)
            if obj.state in [AppMoveGoldTraditional.STATE_EXPIRED]:
                if is_alaisdar_user:
                    actions.append(f'<li><a class="changelink" href="{obj.pk}/renew">{_("state_renew")}</a></li>')                            
            
            # Action for Alaisdar users (Print)
            if obj.state in [AppMoveGoldTraditional.STATE_NEW, AppMoveGoldTraditional.STATE_RENEW, ]:            
                if is_alaisdar_user or is_manager:
                    actions.append(f'<li><a class="changelink" target="_blank" href="{obj.pk}/print">{_("طباعة")}</a></li>')

            # Action for Altarhil users (Arrived)
            is_altarhil_user = False
            try:
                gold_user = request.user.gold_travel_traditional
                if obj.wijhat_altarhil_id in gold_user.goldtraveltraditionaluserjihattarhil_set.values_list('wijhat_altarhil', flat=True):
                    is_altarhil_user = True
            except:
                pass

            if obj.state in [AppMoveGoldTraditional.STATE_NEW, AppMoveGoldTraditional.STATE_RENEW, AppMoveGoldTraditional.STATE_EXPIRED, ]:            
                if is_altarhil_user:
                    actions.append(f'<li><a class="changelink" href="{obj.pk}/arrived">{_("وصل")}</a></li>')

            if not actions:
                return format_html('<ul class="actions-list"><li>&nbsp;</li></ul>')
            
            return format_html('<ul class="actions-list">{links}</ul>', links=format_html(''.join(actions)))

        return get_allowed_actions(obj)

    def changelist_view(self, request, extra_context=None):
        self.current_request = request
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description=_('Export data'))
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="move_gold_form.csv"'},
        )
        header = [
                    _("code"),_("issue_date"),_('gold_weight_in_gram'),_("almustafid_name"),_("almustafid_phone"),
                    _("almustafid_identity_type"), _("almustafid_identity"), _( "jihat_alaisdar"),
                    _("wijhat_altarhil"),_("almushtari_name"),_("source_state"),_("record_state"),_("parent"),
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
                    app.code,app.issue_date,app.gold_weight_in_gram,app.almustafid_name,app.almustafid_phone,
                    app.get_almustafid_identity_type_display(), app.almustafid_identity, app.jihat_alaisdar,
                    app.wijhat_altarhil,app.almushtari_name,app.source_state,app.get_state_display(),parent_code,
                    app.created_at,app.created_by,app.updated_at,app.updated_by,
            ]
            writer.writerow(row)

        return response

admin.site.register(AppMoveGoldTraditional, AppMoveGoldTraditionalAdmin)
