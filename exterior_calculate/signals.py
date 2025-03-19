from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from exterior_calculate.models import ProjectExterior


@receiver(post_save, sender=ProjectExterior)
def update_quantity_correcting(sender, instance, created, **kwargs):
    if instance.exterior_status == 'correcting':
        instance.quantity_correcting += 1
        instance.save()


@receiver(pre_save, sender=ProjectExterior)
def update_in_stock_active(sender, instance, **kwargs):
    if instance.pk:  # Проверяем, что объект уже сохранен в базе данных
        try:
            old_instance = ProjectExterior.objects.get(pk=instance.pk)
            if old_instance.stock_active != instance.stock_active:
                # Если значение поля stock_active изменилось, обновляем поле in_stock_active
                instance.in_stock_active = timezone.now() if instance.stock_active else None
        except ProjectExterior.DoesNotExist:
            pass  # Обработка случая, когда объект еще не сохранен в базе данных
