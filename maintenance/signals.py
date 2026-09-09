from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender='maintenance.StockMovement')
def update_stock_on_movement(sender, instance, created, **kwargs):
    if not created:
        return

    part = instance.spare_part
    if instance.movement_type == 'in':
        part.quantity_in_stock += instance.quantity
    elif instance.movement_type == 'out':
        part.quantity_in_stock = max(0, part.quantity_in_stock - instance.quantity)
    elif instance.movement_type == 'adjust':
        part.quantity_in_stock = instance.quantity

    part.save(update_fields=['quantity_in_stock', 'updated_at'])

    if part.quantity_in_stock <= part.reorder_point:
        from maintenance.models import LowStockAlert, Notification
        today = timezone.now().date()
        alert_exists = LowStockAlert.objects.filter(
            spare_part=part,
            created_at__date=today,
            is_resolved=False
        ).exists()
        if not alert_exists:
            alert = LowStockAlert.objects.create(
                spare_part=part,
                quantity_at_alert=part.quantity_in_stock
            )
            _notify_low_stock(part, alert)


def _notify_low_stock(part, alert):
    from maintenance.models import Notification
    from django.contrib.auth.models import Group

    title   = f"تنبيه: رصيد منخفض — {part.name}"
    message = (
        f"وصل رصيد القطعة [{part.sku}] {part.name} إلى {part.quantity_in_stock} {part.unit_of_measure}، "
        f"وهو أقل من أو يساوي حد الأمان ({part.reorder_point}). يرجى اتخاذ الإجراء اللازم."
    )

    target_groups = ['maintenance_store', 'maintenance_admin']
    for group_name in target_groups:
        try:
            group = Group.objects.get(name=group_name)
            for user in group.user_set.all():
                Notification.objects.create(
                    recipient=user,
                    notification_type='low_stock',
                    title=title,
                    message=message,
                )
        except Group.DoesNotExist:
            pass


@receiver(post_save, sender='maintenance.MaintenanceRequest')
def notify_on_request_status_change(sender, instance, created, **kwargs):
    from maintenance.models import Notification
    from django.contrib.auth.models import Group

    if created:
        if instance.assigned_unit:
            title   = f"طلب صيانة جديد — {instance.request_number}"
            message = (
                f"تم استلام طلب صيانة جديد من {instance.employee_name} "
                f"في {instance.department}. نوع العطل: {instance.fault_category}."
            )
            _notify_group(instance.assigned_unit.group_name, title, message,
                          'request_created', instance)
        return

    if instance.status == 'completed':
        Notification.objects.create(
            recipient=instance.requester,
            notification_type='request_completed',
            title=f"طلبك رقم {instance.request_number} مكتمل",
            message=f"تم إغلاق طلب الصيانة الخاص بك. يُرجى تقييم الخدمة.",
            related_request=instance,
        )
        _notify_group('maintenance_admin',
                      f"إغلاق طلب صيانة — {instance.request_number}",
                      f"تم إغلاق طلب {instance.request_number} بواسطة {instance.assigned_technician}.",
                      'request_completed', instance)


def _notify_group(group_name, title, message, notification_type, request=None):
    from maintenance.models import Notification
    from django.contrib.auth.models import Group

    try:
        group = Group.objects.get(name=group_name)
        for user in group.user_set.all():
            Notification.objects.create(
                recipient=user,
                notification_type=notification_type,
                title=title,
                message=message,
                related_request=request,
            )
    except Group.DoesNotExist:
        pass


from django.contrib.auth.signals import user_logged_in

@receiver(post_save, sender=User)
def auto_assign_maintenance_employee_group(sender, instance, created, **kwargs):
    from django.contrib.auth.models import Group
    try:
        group, _ = Group.objects.get_or_create(name='maintenance_employee')
        if not instance.groups.filter(name='maintenance_employee').exists():
            instance.groups.add(group)
    except Exception:
        pass


@receiver(user_logged_in)
def ensure_maintenance_employee_group_on_login(sender, request, user, **kwargs):
    from django.contrib.auth.models import Group
    try:
        group, _ = Group.objects.get_or_create(name='maintenance_employee')
        if not user.groups.filter(name='maintenance_employee').exists():
            user.groups.add(group)
    except Exception:
        pass

