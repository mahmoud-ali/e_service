from django.contrib import admin
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from executive_office.forms import ContactForm, InboxCompanyForm, TblCompanyProductionEmtiazAutocomplete
from executive_office.models import STATE_DONE, STATE_DRAFT, STATE_PROCESSING, Contact, Inbox, InboxAttachment, InboxCompany, InboxTasks, ProcedureType, ProcedureTypeTasksTemplate, SenderEntity

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    model = Contact
    form = ContactForm
    list_display = ["name","user"]
    search_fields = ["name","user__email"]
    # list_filter = ["company_type"]

class ProcedureTypeTasksTemplateInline(admin.TabularInline):
    model = ProcedureTypeTasksTemplate
    fields = ['title','order','assign_to']
    extra = 1

@admin.register(ProcedureType)
class ProcedureTypeAdmin(admin.ModelAdmin):
    model = ProcedureType
    inlines = [ProcedureTypeTasksTemplateInline]
    list_display = ["name"]
    search_fields = ["name"]

@admin.register(SenderEntity)
class SenderEntityAdmin(admin.ModelAdmin):
    model = SenderEntity
    list_display = ["name"]
    search_fields = ["name"]

class InboxAttachmentInline(admin.TabularInline):
    model = InboxAttachment
    fields = ['attachment_file']
    extra = 1

class InboxCompanyInline(admin.TabularInline):
    model = InboxCompany
    form = InboxCompanyForm
    # fields = ['company']
    extra = 1

class InboxTasksInline(admin.TabularInline):
    model = InboxTasks
    fields = ['title','order','assign_to',]
    extra = 1

    def get_fields(self,request, obj=None):
        if obj and obj.state != STATE_DRAFT:
            return self.fields+['attachment_file','state']
        
        return self.fields

@admin.register(Inbox)
class InboxAdmin(admin.ModelAdmin):
    model = Inbox
    # exclude = ["finish_date","state"]
    fields = ["subject","sender_entity","procedure_type",("start_date","expected_due_date"),"comment"]
    inlines = [InboxAttachmentInline,InboxCompanyInline,InboxTasksInline]
    list_display = ["subject","procedure_type","sender_entity","inbox_companies","start_date","expected_due_date","finish_date","state"]
    search_fields = ["procedure_type__name","sender_entity__name"]
    list_filter = ["procedure_type","sender_entity","state",]

    def change_view(self,request,object_id, form_url='', extra_context=None):
        template = super().change_view(request,object_id, form_url, extra_context)
        if request.POST.get('_save_confirm',None):
            obj = self.get_queryset(request).get(id=object_id)
            obj.state = STATE_PROCESSING
            obj.save()

            obj.inboxtasks_set.all().update(state=STATE_PROCESSING)
            self.log_change(request,obj,_('state_confirmed'))

        return template

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if isinstance(inline,InboxTasksInline):
                if obj:
                    yield formset,inline
            else:
                yield formset,inline

    def has_change_permission(self, request, obj=None):
        if not obj or obj.state != STATE_DRAFT:
            return False
        
        return super().has_change_permission(request,obj)

    def has_delete_permission(self, request, obj=None):
        if not obj or obj.state != STATE_DRAFT:
            return False
        
        return super().has_delete_permission(request,obj)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("company_list/", TblCompanyProductionEmtiazAutocomplete.as_view(),name="lkp_company_emtiaz_list"),
        ]
        return my_urls + urls

    @admin.display(description=_('company'))
    def inbox_companies(self,obj:Inbox):
        l = []
        for rec in obj.inboxcompany_set.all():
            link = f'{rec.company.name_ar}'
            l.append(link)
            
        return format_html(", ".join(l))

@admin.register(InboxTasks)
class InboxTasksAdmin(admin.ModelAdmin):
    model = InboxTasks
    fields = ['title','order','assign_to','comment','attachment_file']
    readonly_fields = ['title','order','assign_to']
    list_display = ['subject','title','order','inbox_companies','inbox_attachments','expected_due_date','state']
    search_fields = ['inbox__subject','title','order','assign_to',]
    list_filter = ["state","assign_to"]

    actions = ['mark_done']

    def change_view(self,request,object_id, form_url='', extra_context=None):
        template = super().change_view(request,object_id, form_url, extra_context)
        if request.POST.get('_save_confirm',None):
            obj = self.get_queryset(request).get(id=object_id)
            obj.state = STATE_DONE
            obj.save()
            self.log_change(request,obj,_('state_confirmed'))

        return template
    
    def get_queryset(self, request):
        qs =  super().get_queryset(request)
        qs = qs.filter(state__gt = STATE_DRAFT)
        return qs

    @admin.display(description=_('expected_due_date'))
    def expected_due_date(self,obj:InboxTasks):
        return obj.inbox.expected_due_date

    @admin.display(description=_('subject'))
    def subject(self,obj:InboxTasks):
        return obj.inbox.subject

    @admin.display(description=_('inbox_attachments'))
    def inbox_attachments(self,obj:InboxTasks):
        l = []
        for rec in obj.inbox.inboxattachment_set.all():
            link = f'<a href="{rec.attachment_file.url}">{rec.attachment_file.name}</a>'
            l.append(link)
            
        return format_html(", ".join(l))
    
    @admin.display(description=_('company'))
    def inbox_companies(self,obj:InboxTasks):
        l = []
        for rec in obj.inbox.inboxcompany_set.all():
            link = f'{rec.company.name_ar}'
            l.append(link)
            
        return format_html(", ".join(l))
    
    # def update_inbox_state(self,obj)
    
    @admin.action(description=_('mark_done'))
    def mark_done(self, request, queryset):
        for obj in queryset:
            if obj.state == STATE_PROCESSING:
                obj.state = STATE_DONE
                obj.save()
                self.message_user(request,_('Record saved successfully.'))

    def has_add_permission(self, request):        
        return False
    
    def has_change_permission(self, request, obj=None):
        if not obj or obj.state == STATE_DONE:
            return False
        
        return super().has_change_permission(request,obj)

    def has_delete_permission(self, request, obj=None):
        if not obj or obj.state != STATE_DRAFT:
            return False
        
        return super().has_delete_permission(request,obj)
