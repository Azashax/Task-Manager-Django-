from django.db import models
from User.models import MyUser
from render.upload_utils import render_image, project_file, floor_plan_render_image, message_correcting_image
from django.utils import timezone

STATUS = (
    ('open', 'open'),
    ('in_progress', 'in_progress'),
    ('complete', 'complete'),
    ('checked', 'checked'),
    ('correcting', 'correcting'),
    ('waiting', 'waiting'),
)


TASK_TYPE = (
    ('render', 'render'),
    ('floor_plan', 'floor_plan'),
)


SUB_TASK_TYPE = (
    ('asset', 'asset'),
    ('geometry', 'geometry'),
    ('render', 'render'),
    ('correcting_2d', 'correcting_2d'),
)

PRIORITY = (
    ('0', '0'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
)

PRIORITY_ENHANCER = (
    ('None', 'None'),
    ('Low Priority', 'Low Priority'),
    ('Medium Priority', 'Medium Priority'),
    ('High Priority', 'High Priority'),
)

ACTION_REQUIRED = (
    ('None', 'None'),
    ('Waiting', 'Waiting'),
    ('Trash', 'Trash'),
)

RENDER_TASK_TEG = (
    ('none', 'none'),
    ('main', 'main'),
)


class ProjectListing(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    user_id = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.SET_NULL,
        related_name='project_user',
        null=True,
        blank=True,
        db_index=True
    )
    employee_id = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.SET_NULL,
        related_name='project_employee',
        null=True,
        blank=True,
        db_index=True
    )
    status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0][0], db_index=True)
    render_check = models.BooleanField(default=False, db_index=True)
    floor_plan_check = models.BooleanField(default=False, db_index=True)
    action_required = models.CharField(max_length=20, choices=ACTION_REQUIRED, default=ACTION_REQUIRED[0][0], db_index=True)
    description = models.TextField(blank=True, null=True)
    sorted = models.BooleanField(default=False, db_index=True)
    listing_amt = models.IntegerField(default=0)
    time_listing_update = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY, default=PRIORITY[0][0], db_index=True)
    priority_enhancer = models.CharField(max_length=20, choices=PRIORITY_ENHANCER, default=PRIORITY_ENHANCER[0][0], db_index=True)
    is_delete = models.BooleanField(default=False, db_index=True)
    time_render_check = models.DateTimeField(null=True, blank=True)
    time_in_progress = models.DateTimeField(null=True, blank=True)
    time_checked = models.DateTimeField(null=True, blank=True)
    time_complete = models.DateTimeField(null=True, blank=True)
    time_correcting = models.DateTimeField(null=True, blank=True)
    update_at = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['user_id']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['status']),
            models.Index(fields=['sorted']),
            models.Index(fields=['priority']),
            models.Index(fields=['priority_enhancer']),
            models.Index(fields=['action_required']),
            models.Index(fields=['is_delete']),
        ]


class ProjectFile(models.Model):
    project_file_id = models.ForeignKey(ProjectListing, on_delete=models.SET_NULL, related_name="project_file", null=True, blank=True)
    file = models.FileField(upload_to=project_file)
    file_info = models.JSONField(blank=True, null=True)

    # def __str__(self):
    #     return self.id


class RenderTaskImages(models.Model):
    task_images_employee_id = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.SET_NULL,
        related_name='task_images_user',
        null=True,
        blank=True
    )
    floor_plan_image = models.ImageField(upload_to=floor_plan_render_image, null=True)
    # desc = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0][0], db_index=True)
    checked_is = models.BooleanField(default=False) #checked_is
    update_at = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}-{self.checked_is}'

    class Meta:
        indexes = [
            models.Index(fields=['task_images_employee_id']),
        ]


class MessageTaskImages(models.Model):
    task_images = models.ForeignKey(RenderTaskImages, on_delete=models.SET_NULL, related_name="task_images_messages", null=True, blank=True, db_index=True)
    user_message = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.SET_NULL,
        related_name='task_message_user',
        null=True,
        blank=True
    )
    desc = models.TextField(null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.task_images}'


class RenderTask(models.Model):
    project_id = models.ForeignKey(ProjectListing, on_delete=models.SET_NULL, related_name="project_task", null=True, blank=True, db_index=True)
    task_employee_id = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.SET_NULL,
        related_name='task_employee',
        null=True,
        blank=True
    )
    task_qa_id = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.SET_NULL,
        related_name='task_qa',
        null=True,
        blank=True
    )
    type = models.CharField(max_length=20, choices=TASK_TYPE)
    image_before = models.ImageField(upload_to=render_image)
    image_before_info = models.JSONField(blank=True, null=True)
    image_after_old = models.ImageField(upload_to=render_image, null=True, blank=True)
    image_after_old_info = models.JSONField(blank=True, null=True)
    image_after = models.ImageField(upload_to=render_image, null=True, blank=True)
    image_after_info = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0][0], db_index=True)
    new_task = models.BooleanField(default=True, db_index=True)   # отметка нового таска для сортировки
    to_begin = models.BooleanField(default=False)   # отметка нового таска для сортировки
    descriptions = models.TextField(blank=True, null=True)
    teg = models.CharField(max_length=20, choices=RENDER_TASK_TEG, default=RENDER_TASK_TEG[0][0], db_index=True)
    image_after_time = models.DateTimeField(null=True, blank=True)
    images = models.ManyToManyField(RenderTaskImages, related_name='task_images', blank=True)

    time_in_progress = models.DateTimeField(null=True, blank=True)
    time_checked = models.DateTimeField(null=True, blank=True)
    time_complete = models.DateTimeField(null=True, blank=True)
    time_correcting = models.DateTimeField(null=True, blank=True)
    update_at = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.project_id} -> {self.type}({self.id})'

    def save(self, *args, **kwargs):
        # Проверяем, если image_after изменился
        if self.pk is not None:  # Объект уже существует в базе данных
            previous = RenderTask.objects.get(pk=self.pk)
            if previous.image_after and self.image_after != previous.image_after:
                # Сохраняем старое значение image_after в image_after_old
                self.image_after_old = previous.image_after
                self.image_after_old_info = previous.image_after_info
                self.image_after_time = timezone.now()  # Обновляем время изменения

        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['project_id']),
            models.Index(fields=['new_task']),
            models.Index(fields=['status']),
        ]


class RenderTaskStatusChange(models.Model):
    task = models.ForeignKey(RenderTask, on_delete=models.SET_NULL, related_name="status_changes", db_index=True, null=True, blank=True)
    original_task_id = models.IntegerField(null=True, blank=True, db_index=True)  # Переименовали поле для хранения id таска
    project_name = models.CharField(max_length=255, null=True, blank=True)  # Сохранение названия проекта
    old_status = models.CharField(max_length=20, choices=STATUS)
    new_status = models.CharField(max_length=20, choices=STATUS)
    changed_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Изменено пользователем")
    changed_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.task:
            self.original_task_id = self.task.id
            if self.task.project_id:
                self.project_name = self.task.project_id.title  # Предполагается, что поле названия проекта называется `title`
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Task {self.original_task_id}: {self.old_status} -> {self.new_status}'

    class Meta:
        indexes = [
            models.Index(fields=['task']),  # Индекс на поле task
            models.Index(fields=['project_name']),  # Индекс для project_name
            models.Index(fields=['changed_at']),  # Индекс для changed_at
        ]


class MessageRenderTask(models.Model):
    render_task = models.ForeignKey(RenderTask, on_delete=models.SET_NULL, related_name="render_task_messages", null=True, blank=True, db_index=True)
    render_task_user_message = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.SET_NULL,
        related_name='render_task_message_user',
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to=message_correcting_image, null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.render_task}'


class SubTask(models.Model):
    task_id = models.ForeignKey(RenderTask, on_delete=models.SET_NULL, related_name="sub_task", null=True, blank=True, db_index=True)
    sub_task_employee_id = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.SET_NULL,
        related_name='sub_task_user',
        null=True,
        blank=True
    )
    sub_task_qa_id = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.SET_NULL,
        related_name='sub_task_qa',
        null=True,
        blank=True
    )
    type = models.CharField(max_length=20, choices=SUB_TASK_TYPE, default=SUB_TASK_TYPE[0][0], db_index=True)
    status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0][0], db_index=True)
    uploaded = models.BooleanField(default=False)
    time_in_progress = models.DateTimeField(null=True, blank=True)
    time_checked = models.DateTimeField(null=True, blank=True)
    time_complete = models.DateTimeField(null=True, blank=True)
    time_correcting = models.DateTimeField(null=True, blank=True)
    update_at = models.DateTimeField(auto_now=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.task_id} -> {self.type}'

    class Meta:
        indexes = [
            models.Index(fields=['task_id']),
            models.Index(fields=['type']),
            models.Index(fields=['status']),
        ]


ACTION_REQUEST = (
    ('get', 'get'),
    ('post', 'post'),
    ('patch', 'patch'),
    ('delete', 'delete'),
)


class StorageActiveUser(models.Model):
    user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.SET_NULL,
        related_name='storage_user',
        null=True,
        blank=True,
        db_index=True
    )
    action = models.CharField(max_length=20, choices=ACTION_REQUEST, db_index=True)
    table = models.CharField(max_length=256, db_index=True)
    fields = models.TextField(db_index=True)
    create_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f'{self.user.id}-{self.action}-{self.fields[:20]}'

    class Meta:
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['user', 'create_at']),
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['fields']),
            models.Index(fields=['create_at']),
        ]
