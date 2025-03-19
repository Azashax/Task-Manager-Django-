from django.core.exceptions import ValidationError


def validate_task_uniqueness(task, instance=None):
    """
    Функция для проверки, что задача не существует в других моделях.
    """
    from .models import UserTaskStock, TaskForReview, UnassignedTasks

    # Проверяем задачу в UserTaskStock, игнорируя текущий экземпляр
    task_stock_qs = UserTaskStock.objects.filter(task=task)
    if instance:
        task_stock_qs = task_stock_qs.exclude(pk=instance.pk)

    if task_stock_qs.exists():
        raise ValidationError(f'Задача {task} уже находится в стоке.')

    # Проверка в TaskForReview
    if TaskForReview.objects.filter(task=task).exists():
        raise ValidationError(f'Задача {task} уже находится на ревью.')

    # Проверка в UnassignedTasks
    if UnassignedTasks.objects.filter(task=task).exists():
        raise ValidationError(f'Задача {task} уже готова для назначения.')