from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _, ngettext

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username','first_name','last_name']
    actions = ['disable_users']

    @admin.action(description=_('Disable selected users'))
    def disable_users(self, request, queryset):
        if request.POST.get('apply'):
            to_disable = queryset.exclude(is_superuser=True).filter(is_active=True)
            count = to_disable.update(is_active=False)
            skipped = queryset.count() - count
            msg = ngettext(
                '%(count)d user was disabled.',
                '%(count)d users were disabled.',
                count,
            ) % {'count': count}
            if skipped:
                msg += ' ' + ngettext(
                    '%(skipped)d selected user was skipped (superuser or already inactive).',
                    '%(skipped)d selected users were skipped (superuser or already inactive).',
                    skipped,
                ) % {'skipped': skipped}
            self.message_user(request, msg, messages.SUCCESS)
            return None

        if request.POST.get('cancel'):
            self.message_user(request, _('Action cancelled. No users were changed.'))
            return None

        # First call from the changelist dropdown: show a confirmation page.
        # With "select all across pages", keep the original selection echoed so
        # the confirm POST still reaches the action; select_across=1 keeps the
        # whole filtered queryset as scope.
        if request.POST.get('select_across'):
            selected_pks = request.POST.getlist(ACTION_CHECKBOX_NAME)
        else:
            selected_pks = list(queryset.values_list('pk', flat=True))
        context = {
            **self.admin_site.each_context(request),
            'title': _('Disable selected users'),
            'queryset': queryset,
            'selected_pks': selected_pks,
            'select_across': bool(request.POST.get('select_across')),
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
            'opts': self.model._meta,
            'to_disable_count': (
                queryset.exclude(is_superuser=True).filter(is_active=True).count()
            ),
        }
        return TemplateResponse(
            request,
            'admin/accounts/customuser/confirm_disable.html',
            context,
        )

admin.site.register(CustomUser, CustomUserAdmin)
