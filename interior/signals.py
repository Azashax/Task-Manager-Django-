from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Task, Project, TaskForReview, UnassignedTasks, UserTaskStock, HistoryTasksTransaction, PriorityTasksStock
from contextlib import contextmanager
from django.db.models import F, Max
from django.utils import timezone
from django.db import transaction

@receiver(pre_save, sender=Task)
def track_task_changes(sender, instance, **kwargs):
    if instance._disable_tracking:  # Если флаг установлен, пропускаем создание истории
        return
    if instance.pk:
        # Получаем старый объект из базы для сравнения
        old_instance = Task.objects.get(pk=instance.pk)

        # Проверяем измененные поля
        for field in ['status', 'type', 'point', 'additional_point', 'total_correcting', 'description']:
            old_value = getattr(old_instance, field)
            new_value = getattr(instance, field)

            if old_value != new_value:
                # Создаем запись в истории изменений
                HistoryTasksTransaction.objects.create(
                    task=instance,
                    changed_by=instance.changed_by,  # Получаем текущего пользователя из локального хранилища
                    field_name=field,
                    old_value=old_value,
                    new_value=new_value,
                    changed_at=timezone.now()
                )


@receiver(post_save, sender=Task)
def log_task_creation(sender, instance, created, **kwargs):
    if created:
        # Логируем создание новой задачи
        HistoryTasksTransaction.objects.create(
            task=instance,
            changed_by=instance.changed_by,  # Получаем текущего пользователя из локального хранилища
            field_name="creation",
            old_value=None,
            new_value="Task created",
            changed_at=timezone.now()
        )
# Сигналы для добавления задач в UnassignedTasks, TaskForReview и UserTaskStock


@receiver(post_save, sender=UnassignedTasks)
def log_unassigned_task(sender, instance, created, **kwargs):
    if created:
        HistoryTasksTransaction.objects.create(
            task=instance.task,
            changed_by=instance.task.changed_by,  # Передайте пользователя из request
            field_name="UnassignedTasks",
            old_value=None,
            new_value="Added to UnassignedTasks",
            changed_at=timezone.now()
        )


@receiver(post_delete, sender=UnassignedTasks)
def log_unassigned_task_deletion(sender, instance, **kwargs):
    HistoryTasksTransaction.objects.create(
        task=instance.task,
        changed_by=instance.task.changed_by,  # Передайте пользователя из request
        field_name="UnassignedTasks",
        old_value="Added to UnassignedTasks",
        new_value="Removed from UnassignedTasks",
        changed_at=timezone.now()
    )


@receiver(post_save, sender=TaskForReview)
def log_task_for_review(sender, instance, created, **kwargs):
    if created:
        HistoryTasksTransaction.objects.create(
            task=instance.task,
            changed_by=instance.task.changed_by,  # Передайте пользователя из request
            field_name="TaskForReview",
            old_value=None,
            new_value="Added to TaskForReview",
            changed_at=timezone.now()
        )


@receiver(post_delete, sender=TaskForReview)
def log_task_for_review_deletion(sender, instance, **kwargs):
    HistoryTasksTransaction.objects.create(
        task=instance.task,
        changed_by=instance.task.changed_by,  # Передайте пользователя из request
        field_name="TaskForReview",
        old_value="Added to TaskForReview",
        new_value="Removed from TaskForReview",
        changed_at=timezone.now()
    )


@receiver(post_save, sender=UserTaskStock)
def log_task_stock(sender, instance, created, **kwargs):
    if created:
        HistoryTasksTransaction.objects.create(
            task=instance.task,
            changed_by=instance.task.changed_by,  # Передайте пользователя из request
            field_name="UserTaskStock",
            old_value=None,
            new_value="Added to UserTaskStock",
            changed_at=timezone.now()
        )


@receiver(post_delete, sender=UserTaskStock)
def log_task_stock_deletion(sender, instance, **kwargs):
    HistoryTasksTransaction.objects.create(
        task=instance.task,
        changed_by=instance.task.changed_by,  # Передайте пользователя из request
        field_name="UserTaskStock",
        old_value="Added to UserTaskStock",
        new_value="Removed from UserTaskStock",
        changed_at=timezone.now()
    )


@receiver(pre_save, sender=Task)
def update_checked_time(sender, instance, **kwargs):
    if instance.pk is not None:
        original_task = Task.objects.get(pk=instance.pk)
        if original_task.status != instance.status:
            if instance.status == 'checked':
                instance.checked_time = timezone.now()
            elif instance.status == 'in progress' and not instance.in_progress_time:
                instance.in_progress_time = timezone.now()
            elif instance.status == 'complete':
                instance.complete_time = timezone.now()
        if original_task.status == 'complete' and instance.status == 'correcting':
            instance.total_correcting = original_task.total_correcting + 1


@receiver(post_save, sender=Project)
def create_tasks(sender, instance, created, **kwargs):
    if created:
        Task.objects.create(
            type='assemble',
            project=instance,
            changed_by=instance.team_lead_user
        )
        Task.objects.create(
            type='without',
            project=instance,
            changed_by=instance.team_lead_user
        )
        Task.objects.create(
            type='with',
            project=instance,
            changed_by=instance.team_lead_user
        )
        Task.objects.create(
            type='upload',
            project=instance,
            changed_by=instance.team_lead_user
        )
        Task.objects.create(
            type='render2d',
            project=instance,
            changed_by=instance.team_lead_user
        )
        Task.objects.create(
            type='2d upload',
            project=instance,
            changed_by=instance.team_lead_user
        )
        # Task.objects.create(
        #     type='render3d',
        #     project=instance
        # )
        instance.save()


@contextmanager
def disable_signal(signal, receiver, sender):
    signal.disconnect(receiver, sender=sender)
    yield
    signal.connect(receiver, sender=sender)


@receiver(pre_save, sender=Task)
def handle_task_pre_save(sender, instance, **kwargs):
    try:
        previous_task = Task.objects.get(pk=instance.pk)
    except Task.DoesNotExist:
        previous_task = None

    if previous_task:
        process_changes(instance, previous_task)
    else:
        handle_new_task(instance)


def process_changes(instance, previous_task):
    if previous_task.point is None and instance.point is not None:
        move_to_unassigned_tasks(instance)

    if previous_task.employee_user != instance.employee_user:
        assign_to_employee(instance)

    if previous_task.status != instance.status:
        status_handlers = {
            "complete": handle_complete,    # del
            "correcting": handle_correcting,    # del
            "restock": handle_restock,
            "rejected": handle_rejected,
            "waiting": handle_waiting,      # del
            "checked": handle_checked,      # del
        }
        handler = status_handlers.get(instance.status, lambda *_: None)
        handler(instance, previous_task)


def handle_new_task(instance):
    if instance.point is not None:
        move_to_unassigned_tasks(instance)
    if instance.employee_user is not None:
        assign_to_employee(instance)


def move_to_unassigned_tasks(instance):
    remove_from_all_models(instance)
    UnassignedTasks.objects.create(task=instance)
    print(f"Task {instance.id} moved to UnassignedTasks.")


def assign_to_employee(instance):
    remove_from_all_models(instance)
    if instance.project.filters_teg.name != "real time":
        position = UserTaskStock.objects.filter(task__employee_user=instance.employee_user).count() + 1
        UserTaskStock.objects.create(task=instance, position=position)
    print(f"Task {instance.id} assigned to {instance.employee_user.username}.")


def handle_complete(instance, previous_task):
    move_to_review(instance)
    adjust_positions(instance.employee_user, get_task_position(instance))
    print(f"Task {instance.id} moved to TaskForReview with status complete.")


def handle_correcting(instance, previous_task):
    remove_from_all_models(instance)
    max_position = get_max_position(instance.employee_user, "correcting")
    with transaction.atomic():
        increment_correction_count(instance)
        adjust_positions(instance.employee_user, max_position + 1, increase=True)
        UserTaskStock.objects.create(task=instance, position=max_position + 1)
    print(f"Task {instance.id} moved to UserTaskStock with status correcting.")


def handle_restock(instance, previous_task):
    assign_to_employee(instance)
    update_task_status(instance, "waiting")
    print(f"Task {instance.id} moved back to UserTaskStock with status waiting.")


def handle_rejected(instance, previous_task):
    move_to_unassigned_tasks(instance)
    adjust_positions(instance.employee_user, get_task_position(instance))
    print(f"Task {instance.id} moved to UnassignedTasks with status rejected.")


def handle_waiting(instance, previous_task):
    move_to_unassigned_tasks(instance)
    adjust_positions(instance.employee_user, get_task_position(instance))
    print(f"Task {instance.id} moved to UnassignedTasks with status waiting.")


def handle_checked(instance, previous_task):
    remove_from_all_models(instance)
    print(f"Task {instance.id} marked as checked and removed from all models.")


def increment_correction_count(instance):
    with disable_signal(pre_save, handle_task_pre_save, Task):
        instance.total_correcting += 1
        instance.save(update_fields=["total_correcting"])


def move_to_review(instance):
    remove_from_all_models(instance)
    TaskForReview.objects.create(task=instance)


def adjust_positions(employee_user, position, increase=False):
    if position is not None:
        adjustment = F("position") + 1 if increase else F("position") - 1
        UserTaskStock.objects.filter(
            task__employee_user=employee_user,
            position__gte=position
        ).update(position=adjustment)


def remove_from_all_models(task):
    print(task)
    UserTaskStock.objects.filter(task=task).delete()
    UnassignedTasks.objects.filter(task=task).delete()
    TaskForReview.objects.filter(task=task).delete()


def update_task_status(task, status):
    with disable_signal(pre_save, handle_task_pre_save, Task):
        task.status = status
        task.save(update_fields=["status"])


def get_task_position(instance):
    task_stock = UserTaskStock.objects.filter(task=instance).first()
    return task_stock.position if task_stock else None


def get_max_position(employee_user, status):
    return UserTaskStock.objects.filter(
        task__employee_user=employee_user,
        task__status=status
    ).aggregate(Max("position"))["position__max"] or 0


# @contextmanager
# def disable_signal(signal, receiver, sender):
#     signal.disconnect(receiver, sender=sender)
#     yield
#     signal.connect(receiver, sender=sender)
#
#
# @receiver(pre_save, sender=Task)
# def handle_task_pre_save(sender, instance, **kwargs):
#     try:
#         previous_task = Task.objects.get(pk=instance.pk)
#     except Task.DoesNotExist:
#         # Новая задача, пропускаем
#         previous_task = None
#     # 1. Изменение `point` с пустого на что-то
#     if previous_task is None and instance.point is not None:
#         handle_point_change(instance, previous_task)
#     elif previous_task and previous_task.point is None and instance.point is not None:
#         handle_point_change(instance, previous_task)
#
#     # 2. Изменение `employee_user`
#     if previous_task is None and instance.employee_user is not None:
#         handle_employee_user_change(instance, previous_task)
#     elif previous_task and previous_task.employee_user != instance.employee_user and instance.employee_user is not None:
#         handle_employee_user_change(instance, previous_task)
#
#     # 3. Изменение статуса задачи
#     # Множество статусов, при которых handle_status_change не вызывается
#     excluded_statuses = {"on test", "in progress", "open"}
#     if previous_task and previous_task.status != instance.status and instance.status not in excluded_statuses:
#         handle_status_change(instance, previous_task)
#
#
# def handle_point_change(instance, previous_task):
#     """
#     Логика обработки изменения `point`.
#     """
#     remove_task_from_all(instance)
#     UnassignedTasks.objects.create(task=instance)
#     print(f'Task {instance.id} добавлена в UnassignedTasks из-за изменения point.')
#
#
# def handle_employee_user_change(instance, previous_task):
#     """
#     Логика обработки изменения `employee_user`.
#     """
#     remove_task_from_all(instance)
#     if instance.project.filters_teg.name != "real time":
#         count_task = UserTaskStock.objects.filter(task__employee_user=instance.employee_user).count()
#         UserTaskStock.objects.create(task=instance, position=count_task+1)
#     print(f'Task {instance.id} добавлена в UserTaskStock для пользователя {instance.employee_user.username}.')
#
#
# def handle_status_change(instance, previous_task):
#     """
#     Логика обработки изменения статуса задачи.
#     """
#     status = instance.status
#     task_stock = UserTaskStock.objects.filter(task=instance).first()
#     position_to_remove = task_stock.position if task_stock else None
#     # Удаляем задачу из всех других моделей перед любыми изменениями
#     remove_task_from_all(instance)
#
#     if status == 'complete':
#         with transaction.atomic():
#             # Перемещаем задачу в TaskForReview
#             TaskForReview.objects.create(task=instance)
#
#             if position_to_remove is not None:
#                 # Понижаем позицию для всех задач, следующих за текущей
#                 UserTaskStock.objects.filter(
#                     task__employee_user=instance.employee_user,
#                     position__gte=position_to_remove
#                 ).update(position=F('position') - 1)
#
#         print(f'Task {instance.id} перемещена в TaskForReview со статусом complete.')
#
#     elif status == 'correcting':
#         max_position = UserTaskStock.objects.filter(
#             task__employee_user=instance.employee_user,
#             task__status="correcting"
#         ).aggregate(Max('position'))['position__max'] or 0
#         with transaction.atomic():
#             with disable_signal(pre_save, handle_task_pre_save, Task):
#                 HistoryTasksTransaction.objects.create(
#                     task=instance,
#                     changed_by=instance.changed_by,
#                     field_name="total_correcting",
#                     old_value=instance.total_correcting,
#                     new_value=instance.total_correcting + 1,
#                     changed_at=timezone.now()
#                 )
#                 instance._disable_tracking = True
#                 instance.total_correcting += 1
#                 instance.save(update_fields=["total_correcting"])
#                 instance._disable_tracking = False
#             UserTaskStock.objects.filter(task__employee_user=instance.employee_user, position__gte=max_position+1).update(
#                 position=F('position') + 1)
#             UserTaskStock.objects.create(task=instance, position=max_position+1)
#         print(f'Task {instance.id} возвращена в UserTaskStock со статусом correcting.')
#
#     elif status == 'restock':
#         # Возвращаем задачу в UserTaskStock
#         count_task = UserTaskStock.objects.filter(task__employee_user=instance.employee_user).count()
#         UserTaskStock.objects.create(task=instance, position=count_task+1)
#         with disable_signal(pre_save, handle_task_pre_save, Task):
#             instance.status = 'waiting'
#             instance.save(update_fields=['status'])
#         print(f'Task {instance.id} возвращена в UserTaskStock со статусом waiting.')
#
#     elif status == 'rejected':
#         # Перемещаем задачу в UnassignedTasks
#         with transaction.atomic():
#             UnassignedTasks.objects.create(task=instance)
#             if position_to_remove is not None:
#                 # Понижаем позицию для всех задач, следующих за текущей
#                 UserTaskStock.objects.filter(
#                     task__employee_user=instance.employee_user,
#                     position__gte=position_to_remove
#                 ).update(position=F('position') - 1)
#         with disable_signal(pre_save, handle_task_pre_save, Task):
#             instance.status = 'waiting'
#             instance.save(update_fields=['status'])
#         print(f'Task {instance.id} возвращена в UnassignedTasks со статусом waiting.')
#
#     elif status == 'waiting':
#         # Перемещаем задачу в UnassignedTasks
#         with transaction.atomic():
#             UnassignedTasks.objects.create(task=instance)
#             if position_to_remove is not None:
#                 # Понижаем позицию для всех задач, следующих за текущей
#                 UserTaskStock.objects.filter(
#                     task__employee_user=instance.employee_user,
#                     position__gte=position_to_remove
#                 ).update(position=F('position') - 1)
#         print(f'Task {instance.id} перемещена в UnassignedTasks со статусом waiting.')
#
#     elif status == 'checked':
#         # Задача считается завершенной и удалена из всех моделей
#         print(f'Task {instance.id} завершена и удалена из всех моделей со статусом checked.')
#
#
# def remove_task_from_all(task):
#     """
#     Удаляет задачу из всех моделей, где она может находиться.
#     """
#     UserTaskStock.objects.filter(task=task).delete()
#     UnassignedTasks.objects.filter(task=task).delete()
#     TaskForReview.objects.filter(task=task).delete()
