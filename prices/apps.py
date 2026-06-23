from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


def setup_prices_groups(sender, **kwargs):
    """Create role-based groups for the prices app."""
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    from prices.models import (
        GlobalGoldPrice,
        BankSudanGoldPrice,
        StateGoldPrice,
        DollarPrice,
    )

    groups_config = {
        'prices_main': {
            'label': _('مدخلي الأسعار الرئيسية'),
            'models': [GlobalGoldPrice, BankSudanGoldPrice, DollarPrice],
            'actions': ['add', 'change', 'view', 'delete'],
        },
        'prices_parallel_dollar': {
            'label': _('مدخلي سعر الدولار الموازي'),
            'models': [DollarPrice],
            'actions': ['add', 'change', 'view'],
        },
        'prices_state_gold': {
            'label': _('مدخلي أسعار الذهب بالولايات'),
            'models': [StateGoldPrice],
            'actions': ['add', 'change', 'view'],
        },
        'prices_viewer': {
            'label': _('مستعرضي الأسعار'),
            'models': [GlobalGoldPrice, BankSudanGoldPrice, StateGoldPrice, DollarPrice],
            'actions': ['view'],
        },
    }

    for group_name, config in groups_config.items():
        group, created = Group.objects.get_or_create(name=group_name)
        perms_to_add = []

        for model in config['models']:
            content_type = ContentType.objects.get_for_model(model)
            for action in config['actions']:
                codename = f"{action}_{model._meta.model_name}"
                try:
                    perm = Permission.objects.get(
                        codename=codename,
                        content_type=content_type,
                    )
                    perms_to_add.append(perm)
                except Permission.DoesNotExist:
                    pass

        group.permissions.set(perms_to_add)


class PricesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prices'
    verbose_name = _('رصد ومراقبة الأسعار')

    def ready(self):
        post_migrate.connect(setup_prices_groups, sender=self)
