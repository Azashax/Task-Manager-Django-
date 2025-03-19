from django.db import models
from User.models import MyUser
from .upload_paths import task_files, task_images, message_images
from django.db import transaction
from .models_validate import validate_task_uniqueness
from django.core.exceptions import ValidationError
from django.utils import timezone

STATUS = (
    ('open', 'open'),
    ('in progress', 'in progress'),
    ('complete', 'complete'),
    ('on test', 'on test'),
    ('checked', 'checked'),
    ('correcting', 'correcting'),
    ('waiting', 'waiting'),
    ('restock', 'restock'),
    ('rejected', 'rejected'),
)

PRIORITY = (
    ('None', 'None'),
    ('Low Priority', 'Priority'),
    ('Midl priority', 'Midl priority'),
    ('High priority', 'High priority'),
)

PROJECT_TYPE = (
    ('Tower', 'Tower'),
    ('Villa', 'Villa'),
)

BUILT = (
    ('finished', 'finished'),
    ('off plan', 'off plan'),
)

EXTERIOR_STATUS = (
    ('open', 'open'),
    ('in progress', 'in progress'),
    ('checked', 'checked'),
)


class ProjectsFilterTeg(models.Model):
    teg = models.CharField(max_length=256)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.teg


class Region(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    team_lead_user = models.ForeignKey(
        MyUser,
        verbose_name='Team Lead',
        on_delete=models.SET_NULL,
        limit_choices_to={'role': 'InteriorTeamLead'},
        related_name='interior_project_team_lead_user',
        null=True,
        blank=True,
        db_index=True
    )

    title = models.CharField(max_length=255, db_index=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, related_name="region", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0][0])

    # marker built tower
    built = models.CharField(max_length=20, choices=BUILT, default=BUILT[0][0])

    # type Tower and Villa
    type = models.CharField(max_length=20, choices=PROJECT_TYPE, default=PROJECT_TYPE[0][0])

    # priority list
    filter_teg = models.ForeignKey(ProjectsFilterTeg, related_name="filters_teg", on_delete=models.SET_NULL, blank=True, null=True)

    # info links
    link_click_up = models.TextField(blank=True, null=True)
    link_cet3 = models.TextField(blank=True, null=True)

    # Описание
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['team_lead_user']),
            models.Index(fields=['type']),
            models.Index(fields=['status']),
        ]


class Task(models.Model):
    TASK_TYPE = (
        ('none', 'none'),
        ('assemble', 'assemble'),
        ('without', 'without'),
        ('with', 'with'),
        ('gltf', 'gltf'),
        ('upload', 'upload'),
        ('render2d', 'render2d'),
        ('2d upload', '2d upload'),
    )

    employee_user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь Employee',
        on_delete=models.SET_NULL,
        limit_choices_to={'role': 'InteriorEmployee'},
        related_name='tasks_as_employee',
        null=True,
        blank=True,
        db_index=True
    )

    qa_user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь QA',
        on_delete=models.SET_NULL,
        related_name='tasks_as_qa',
        null=True,
        blank=True,
        db_index=True
    )

    changed_by = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь изменивший задачу',
        on_delete=models.SET_NULL,
        related_name='task_changed_by',
        null=True,
        blank=True
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        related_name="tasks",
        blank=True,
        null=True,
        db_index=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default=STATUS[0][0],
        db_index=True
    )

    type = models.CharField(
        max_length=20,
        choices=TASK_TYPE,
        db_index=True
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY,
        default=PRIORITY[0][0],
        db_index=True
    )

    # Время
    in_progress_time = models.DateTimeField(null=True, blank=True)
    checked_time = models.DateTimeField(null=True, blank=True)
    complete_time = models.DateTimeField(null=True, blank=True)

    # start_time = models.DateTimeField(null=True, blank=True)
    # total_worked_seconds = models.IntegerField(default=0)
    # Оценочные баллы
    point = models.FloatField(null=True, blank=True)

    # дополнительные баллы
    additional_point = models.FloatField(null=True, blank=True)

    # Количество исправлений
    total_correcting = models.IntegerField(default=0)

    # Дополнительные данные (динамические)
    info_data = models.JSONField(blank=True, null=True)

    # Описание
    description = models.TextField(blank=True, null=True)
    _disable_tracking = False

    def __str__(self):
        return f'{self.project} -> {self.type}'

    class Meta:
        ordering = ['id']
        # Улучшение индексов
        indexes = [
            models.Index(fields=['employee_user']),
            models.Index(fields=['qa_user']),
            models.Index(fields=['project']),
            models.Index(fields=['status']),
            models.Index(fields=['type']),
        ]


class TaskImages(models.Model):
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, related_name="task_image",
                                      null=True, blank=True)
    file = models.FileField(upload_to=task_images)
    file_info = models.JSONField(blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id


class TaskFiles(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="task_file",
                             null=True, blank=True)
    file = models.FileField(upload_to=task_files)
    file_info = models.JSONField(blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id


class PriorityTasksStock(models.Model):
    users = models.ManyToManyField(
        MyUser,
        verbose_name='Пользователи для выполнения задач',
        related_name='user_priority_tasks',
        blank=True
    )
    tasks = models.ManyToManyField(
        Task,
        related_name="priority_tasks",
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PriorityTasksStock {self.id}"


class UserTaskStock(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='task_stock')
    position = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']
        indexes = [
            models.Index(fields=['task']),
            models.Index(fields=['position']),
        ]

    def __str__(self):
        return f'{self.task} (Позиция: {self.position})'

    def clean(self):
        super().clean()

        # Проверяем уникальность задачи
        validate_task_uniqueness(self.task, instance=self)


class TaskForReview(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='task_for_review')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Task {self.task.id} for review'

    def clean(self):
        super().clean()

        # Проверяем уникальность задачи
        validate_task_uniqueness(self.task)


class UnassignedTasks(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='ready_for_assignment', default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Task {self.task.id} is ready for assignment'

    def clean(self):
        super().clean()

        # Проверяем уникальность задачи
        validate_task_uniqueness(self.task)


class HistoryTasksTransaction(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='history_transactions',
        db_index=True)
    changed_by = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь изменивший задачу',
        on_delete=models.SET_NULL,
        related_name='history_transactions',
        null=True,
        blank=True, db_index=True)
    field_name = models.CharField(max_length=50, verbose_name='Измененное поле', db_index=True)
    old_value = models.TextField(null=True, blank=True, verbose_name='Старое значение', db_index=True)
    new_value = models.TextField(null=True, blank=True, verbose_name='Новое значение', db_index=True)
    changed_at = models.DateTimeField(default=timezone.now, verbose_name='Время изменения', db_index=True)

    def __str__(self):
        return f'Изменение {self.field_name} для задачи {self.task.id} от {self.changed_by}'

    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['task']),
            models.Index(fields=['changed_by']),
            models.Index(fields=['field_name']),
            models.Index(fields=['old_value']),
            models.Index(fields=['new_value']),
            models.Index(fields=['changed_at']),
        ]


class TaskMessage(models.Model):
    user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.SET_NULL,
        related_name='task_messages',
        null=True,
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        related_name="task_messages",
        null=True,
    )
    number_correcting = models.IntegerField(default=0)
    message = models.CharField(max_length=1024, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.task.project} ({self.task.type}) -> {self.user.username}'


class MessageImage(models.Model):
    task_message = models.ForeignKey(
        TaskMessage,
        on_delete=models.SET_NULL,
        related_name="task_message_images",
        null=True,
    )
    img = models.ImageField(upload_to=message_images, null=True, blank=True)  # Добавил путь загрузки

    def __str__(self):
        return f"Image {self.id}"