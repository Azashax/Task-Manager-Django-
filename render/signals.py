from django.db.models.signals import post_save, pre_save, post_delete
from django.utils import timezone
from .models import ProjectListing, RenderTask, ProjectFile, RenderTaskImages, SubTask, StorageActiveUser, RenderTaskStatusChange
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image
from django.dispatch import receiver
from django.db.models import Q
import os
import mimetypes
import logging
logger = logging.getLogger(__name__)
from django.db import transaction
import requests
from io import BytesIO

@receiver(pre_save, sender=RenderTask)
def create_status_change_record(sender, instance, **kwargs):
    if instance.pk:  # Check if the instance exists (i.e., it's an update)
        try:
            previous_task = RenderTask.objects.select_related('project_id').get(pk=instance.pk)
            old_status = previous_task.status

            if old_status != instance.status:
                last_correcting_2d_subtask = previous_task.sub_task.select_related('sub_task_employee_id').first()

                with transaction.atomic():
                    RenderTaskStatusChange.objects.create(
                        task=instance,
                        original_task_id=instance.id,
                        project_name=instance.project_id.title if instance.project_id else None,
                        old_status=old_status,
                        new_status=instance.status,
                        changed_by=last_correcting_2d_subtask.sub_task_employee_id if last_correcting_2d_subtask else None
                    )

        except RenderTask.DoesNotExist:
            # Handle the case where the task does not exist, which is unexpected during an update
            pass


@receiver(post_save, sender=ProjectListing)
def update_project_name_in_status_changes(sender, instance, **kwargs):
    # Обновляем названия проекта во всех связанных записях RenderTaskStatusChange
    RenderTaskStatusChange.objects.filter(task__project_id=instance).update(project_name=instance.title)


@receiver(pre_save, sender=RenderTask)
def update_checked_time(sender, instance, **kwargs):
    if instance.pk is not None:
        original_task = RenderTask.objects.get(pk=instance.pk)

        if original_task.status != instance.status:
            if instance.status == 'checked':
                instance.time_checked = timezone.now()
            elif instance.status == 'in_progress' and not instance.time_in_progress:
                instance.in_progress_time = timezone.now()
            elif instance.status == 'complete':
                instance.time_complete = timezone.now()
            elif instance.status == 'correcting':
                instance.time_correcting = timezone.now()


@receiver(pre_save, sender=SubTask)
def update_checked_time(sender, instance, **kwargs):
    if instance.pk is not None:
        original_task = SubTask.objects.get(pk=instance.pk)

        if original_task.status != instance.status:
            if instance.status == 'checked':
                instance.time_checked = timezone.now()
            elif instance.status == 'in_progress' and not instance.time_in_progress:
                instance.in_progress_time = timezone.now()
            elif instance.status == 'complete':
                instance.time_complete = timezone.now()
            elif instance.status == 'correcting':
                instance.time_correcting = timezone.now()


@receiver(pre_save, sender=ProjectListing)
def update_checked_time(sender, instance, **kwargs):
    if instance.pk is not None:
        original_task = ProjectListing.objects.get(pk=instance.pk)

        if original_task.status != instance.status:
            if instance.status == 'checked':
                instance.time_checked = timezone.now()
            elif instance.status == 'in_progress' and not instance.time_in_progress:
                instance.time_in_progress = timezone.now()
            elif instance.status == 'complete':
                instance.time_complete = timezone.now()
            elif instance.status == 'correcting':
                instance.time_correcting = timezone.now()

        if original_task.listing_amt != instance.listing_amt:
            instance.time_listing_update = timezone.now()

        if original_task.render_check != instance.render_check:
            instance.time_render_check = timezone.now()


# def get_image_info_from_url(image_url):
#     try:
#         # Выполняем HTTP-запрос для получения изображения
#         response = requests.get(f'https://d1kpxe5geks6lx.cloudfront.net/{image_url}')
#         print("signals", response)
#         if response.status_code == 200:
#             file_data = response.content  # Получаем данные файла
#
#             # Используем PIL для работы с изображением
#             image = Image.open(BytesIO(file_data))
#             width, height = image.size
#
#             # Информация о файле
#             file_size_mb = len(file_data)
#             file_extension = image.format.lower()
#             modification_time = response.headers.get('Last-Modified', 'Unknown')
#
#             # Возвращаем информацию об изображении
#             return {
#                 "width": width,
#                 "height": height,
#                 "file_size_mb": file_size_mb,
#                 "file_extension": f".{file_extension}",
#                 "modification_time": modification_time,
#             }
#         else:
#             print(f"Error retrieving image: HTTP {response.status_code}")
#             return None
#     except Exception as e:
#         print(f"Error retrieving image info: {e}")
#         return None
#
#
# def update_image_info(instance, image, field_name):
#     if image:
#         image_info = get_image_info_from_url(image.url)
#         setattr(instance, f"{field_name}_info", image_info)
#
# @receiver(post_save, sender=RenderTask)
# def save_image_info(sender, instance, created, **kwargs):
#     # Получаем предыдущую версию объекта из базы данных
#     try:
#         previous_instance = RenderTask.objects.get(pk=instance.pk)
#     except RenderTask.DoesNotExist:
#         previous_instance = None
#     # Проверяем изменение изображения image_before
#     if not previous_instance or previous_instance.image_before != instance.image_before:
#         update_image_info(instance, instance.image_before, 'image_before')
#     # Проверяем изменение изображения image_after
#     # if not previous_instance or previous_instance.image_after != instance.image_after:
#     #     update_image_info(instance, instance.image_after, 'image_after')
#     # Сохраняем только если информация обновилась
#     if previous_instance:
#         instance.save(update_fields=['image_before_info'])  # update_fields=['image_before_info', 'image_after_info']


# Функция для удаления старого файла из S3
def delete_old_file(instance, field_name):
    try:
        # Получаем старый файл
        old_file = getattr(instance, field_name)
        if old_file:
            # Удаляем файл из S3
            old_file.delete(save=False)
            logger.info(f"Файл {old_file} успешно удален.")
    except ObjectDoesNotExist:
        logger.warning(f"Объект не существует: {instance}")
    except Exception as e:
        logger.error(f"Ошибка при удалении файла {old_file}: {e}")

# Сигнал pre_save для модели RenderTaskImages
@receiver(pre_save, sender=RenderTaskImages)
def delete_old_floor_plan_image(sender, instance, **kwargs):
    if instance.pk:
        # Если объект уже существует, то удаляем старый файл
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.floor_plan_image != instance.floor_plan_image:
            delete_old_file(old_instance, 'floor_plan_image')
            logger.info(f"Удален старый floor_plan_image для {instance}.")

# Сигнал pre_save для модели RenderTask
@receiver(pre_save, sender=RenderTask)
def delete_old_render_task_images(sender, instance, **kwargs):
    if instance.pk:
        # Если объект уже существует, то удаляем старые файлы
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.image_before != instance.image_before:
            delete_old_file(old_instance, 'image_before')
            logger.info(f"Удален старый image_before для {instance}.")
        if old_instance.image_after_old != instance.image_after_old:
            delete_old_file(old_instance, 'image_after_old')
            logger.info(f"Удален старый image_after_old для {instance}.")

# Сигнал post_delete для модели RenderTaskImages
@receiver(post_delete, sender=RenderTaskImages)
def delete_file_on_render_task_images_delete(sender, instance, **kwargs):
    delete_old_file(instance, 'floor_plan_image')
    logger.info(f"Удален floor_plan_image после удаления {instance}.")

# Сигнал post_delete для модели RenderTask
@receiver(post_delete, sender=RenderTask)
def delete_files_on_render_task_delete(sender, instance, **kwargs):
    delete_old_file(instance, 'image_before')
    delete_old_file(instance, 'image_after')
    logger.info(f"Удалены image_before и image_after после удаления {instance}.")


