from django.db import models
from datetime import datetime, timedelta

STATUS = (
    ('open', 'open'),
    ('in progress', 'in progress'),
    ('complete', 'complete'),
    ('checked', 'checked'),
    ('correcting', 'correcting'),
    ('waiting', 'waiting'),
)

# Роли сотрудников
class Role(models.Model):
    title = models.CharField(max_length=255)
    typeTask = models.ManyToManyField('TaskData', related_name='role')  # Связь с ролями
    objects = models.Manager()

    def __str__(self):
        return self.title


# Пользователь
class UserProduct(models.Model):
    name = models.CharField(max_length=255)  # Имя виртуального пользователя
    roles = models.ManyToManyField(Role, related_name='user_products')  # Связь с ролями
    objects = models.Manager()

    def __str__(self):
        return self.name  # Отображение имени в админке


class Project(models.Model):
    title = models.CharField(max_length=255)
    tariff = models.ForeignKey('Tariff', related_name='project', on_delete=models.CASCADE, blank=True, null=True)
    money = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Бюджет
    time = models.FloatField(blank=True, null=True)  # Время выполнения проекта
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    project = models.ForeignKey(Project, related_name='products', on_delete=models.CASCADE)
    time = models.FloatField(blank=True, null=True)  # Время выполнения
    money = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Стоимость
    # product_data = models.ManyToManyField('ProductData', related_name='products', blank=True)
    type = models.ForeignKey('TypeData', related_name='products', on_delete=models.CASCADE, blank=True, null=True)
    fields = models.JSONField(default=dict, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return self.title


class ArchiveTaskManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archive_is=False)


class Task(models.Model):
    title = models.CharField(max_length=255)
    product = models.ForeignKey(Product, related_name='tasks', on_delete=models.CASCADE)
    duration = models.FloatField(blank=True, null=True)  # Длительность выполнения задачи
    money_per_hour = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Оплата за час
    # user = models.ForeignKey(UserProduct, on_delete=models.CASCADE, related_name='tasks', blank=True, null=True)  # Назначенные сотрудники
    task_data = models.ForeignKey('TaskData', on_delete=models.CASCADE, related_name='tasks', blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    archive_is = models.BooleanField(default=False)    # Архив
    # status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0][0], db_index=True)

    objects = models.Manager()


    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['archive_is']),  # Индекс на поле arxiv_is
            models.Index(fields=['product', 'created_at']),  # Составной индекс
        ]
        ordering = ['-created_at']  # Сортировка по умолчанию


class SubTask(models.Model):
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=50,
        choices=[('todo', 'To Do'), ('in_progress', 'In Progress'), ('done', 'Done')],
        default='todo'
    )
    user = models.ForeignKey(UserProduct, on_delete=models.CASCADE, related_name='subtasks')  # Кто выполняет задачу
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    time_spent = models.PositiveIntegerField(default=0, help_text="Time spent in minutes")
    waiting_time = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.parent_task.title} -> {self.title}"


class Tariff(models.Model):
    title = models.CharField(max_length=255)
    product_data = models.ManyToManyField('ProductData', related_name='tariff', blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return self.title


class TypeData(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class ProductData(models.Model):
    title = models.CharField(max_length=255)
    task_group_data = models.ManyToManyField('TaskGroupData', related_name='product_data', blank=True)
    task_data = models.ManyToManyField('TaskData', related_name='product_data', blank=True)
    type = models.ManyToManyField(TypeData, related_name='product_data', blank=True)
    position = models.IntegerField(blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return self.title


class TaskGroupData(models.Model):
    title = models.CharField(max_length=255)
    task_data = models.ManyToManyField('TaskData', related_name='task_group_data', blank=True)  # Подходящие роли
    fields = models.JSONField(default=dict, blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return self.title


class TaskData(models.Model):
    title = models.CharField(max_length=255)
    duration = models.JSONField(default=dict, blank=True, null=True)
    money_per_hour = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    several = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks'
    )
    position = models.IntegerField(blank=True, null=True)
    objects = models.Manager()

    def __str__(self):
        return self.title