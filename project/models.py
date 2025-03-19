from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from User.models import MyUser
from project.utils_upload import message_image


STATUS = (
    ('open', 'open'),
    ('in progress', 'in progress'),
    ('complete', 'complete'),
    ('checked', 'checked'),
    ('correcting', 'correcting'),
    ('waiting', 'waiting'),
)

TEG = (
    ('None', 'None'),
    ('Priority', 'Priority'),
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


class Project(models.Model):
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE, default="Tower")
    project_teamlead_user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Teamlead'},
        related_name='project_teamlead_user',
        null=True,
        blank=True,
        db_index=True
    )
    project_name = models.CharField(max_length=255, db_index=True)
    region = models.ForeignKey("Region", on_delete=models.CASCADE, related_name="region", blank=True, null=True)
    built = models.CharField(max_length=20, choices=BUILT, default=BUILT[0][0])
    project_status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0][0])
    link_clickup = models.TextField()
    link_cet3 = models.TextField()
    project_teg = models.CharField(max_length=20, choices=TEG, default="None")
    filter_teg = models.ForeignKey(ProjectsFilterTeg, on_delete=models.SET_NULL, blank=True, null=True)
    exterior_status = models.CharField(max_length=20, choices=EXTERIOR_STATUS, default=STATUS[0][0])

    description = models.TextField(blank=True, null=True)

    task_with = models.OneToOneField("Task", on_delete=models.SET_NULL, related_name="task_with", blank=True, null=True, db_index=True)
    task_without = models.OneToOneField("Task", on_delete=models.SET_NULL, related_name="task_without", blank=True, null=True, db_index=True)
    task_assemble = models.OneToOneField("Task", on_delete=models.SET_NULL, related_name="task_assemble", blank=True, null=True, db_index=True)
    task_gltf = models.OneToOneField("Task", on_delete=models.SET_NULL, related_name="task_gltf", blank=True, null=True, db_index=True)
    task_upload = models.OneToOneField("Task", on_delete=models.SET_NULL, related_name="task_upload", blank=True, null=True, db_index=True)
    task_render2d = models.OneToOneField("Task", on_delete=models.SET_NULL, related_name="task_render2d", blank=True, null=True, db_index=True)
    task_render2d_upload = models.OneToOneField("Task", on_delete=models.SET_NULL, related_name="task_render2d_upload", blank=True, null=True, db_index=True)
    task_render3d = models.OneToOneField("Task", on_delete=models.SET_NULL, related_name="task_render3d", blank=True, null=True, db_index=True)

    def __str__(self):
        return self.project_name

    def save(self, *args, **kwargs):
        if self.project_type == "Villa":
            self.task_assemble = None
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['project_name']),
            models.Index(fields=['project_teamlead_user']),
            models.Index(fields=['task_with']),
            models.Index(fields=['task_without']),
            models.Index(fields=['task_assemble']),
            models.Index(fields=['task_gltf']),
            models.Index(fields=['task_upload']),
            models.Index(fields=['task_render2d']),
            models.Index(fields=['task_render2d_upload']),
            models.Index(fields=['task_render3d']),
        ]


@receiver(post_save, sender=Project)
def create_tasks(sender, instance, created, **kwargs):
    if created:
        task_with = Task.objects.create(
            task_type='with',
            project_task_name=instance.project_name,
            project_id=instance.id
        )
        instance.task_with = task_with

        task_gltf = Task.objects.create(
            task_type='gltf',
            project_task_name=instance.project_name,
            project_id=instance.id
        )
        instance.task_gltf = task_gltf

        task_without = Task.objects.create(
            task_type='without',
            project_task_name=instance.project_name,
            project_id=instance.id
        )
        instance.task_without = task_without

        task_upload = Task.objects.create(
            task_type='upload',
            project_task_name=instance.project_name,
            project_id=instance.id
        )
        instance.task_upload = task_upload

        task_render2d = Task.objects.create(
            task_type='render2d',
            project_task_name=instance.project_name,
            project_id=instance.id
        )
        instance.task_render2d = task_render2d

        task_render2d_upload = Task.objects.create(
            task_type='render2d_upload',
            project_task_name=instance.project_name,
            project_id=instance.id
        )
        instance.task_render2d_upload = task_render2d_upload

        task_render3d = Task.objects.create(
            task_type='render3d',
            project_task_name=instance.project_name,
            project_id=instance.id
        )
        instance.task_render3d = task_render3d

        if instance.project_type != "Villa":
            task_assemble = Task.objects.create(
                task_type='assemble',
                project_task_name=instance.project_name,
                project_id=instance.id
            )
            instance.task_assemble = task_assemble
        instance.save()


class Task(models.Model):
    TASK_TYPE = (
        ('none', 'none'),
        ('with', 'with'),
        ('without', 'without'),
        ('gltf', 'gltf'),
        ('assemble', 'assemble'),
        ('upload', 'upload'),
        ('render2d', 'render2d'),
        ('render2d_upload', 'render2d_upload'),
        ('render3d', 'render3d'),
    )
    TASK_TYPE_GROUP = (
        ('projects', 'projects'),
        ('no projects', 'no projects'),
    )
    task_employee_user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Employee'},
        related_name='task_employee_user',
        null=True,
        blank=True,
        db_index=True
    )
    task_correcting_employee_user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь Correcting',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'Employee'},
        related_name='task_correcting_employee_user',
        null=True,
        blank=True
    )
    check_out_user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь Check Out',
        on_delete=models.CASCADE,
        related_name='task_check_out_user',
        null=True,
        blank=True,
        db_index=True
    )
    check_out = models.BooleanField(default=False)
    project_task_name = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    project_id = models.CharField(max_length=100, null=True, blank=True)
    task_status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0][0], db_index=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPE, default=TASK_TYPE[0][0], db_index=True)
    task_type_group = models.CharField(max_length=20, choices=TASK_TYPE_GROUP, default=TASK_TYPE_GROUP[0][0], db_index=True)
    in_progress_time = models.DateTimeField(null=True, blank=True)
    in_stock_active = models.DateTimeField(null=True, blank=True)
    checked_time = models.DateTimeField(null=True, blank=True)
    complete_time = models.DateTimeField(null=True, blank=True)
    point = models.FloatField(null=True, blank=True)
    time_point = models.CharField(max_length=100, null=True, blank=True)
    additional_time_point = models.IntegerField(default=0)
    correcting_point = models.FloatField(null=True, blank=True)
    time_correcting_point = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    stock_active = models.BooleanField(default=False, db_index=True)
    project_teg = models.CharField(max_length=20, choices=TEG, default="None", db_index=True)
    total_correcting = models.IntegerField(default=0)
    # json_data = models.JSONField(default=[])
    json_data_calculate = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'{self.project_task_name} -> {self.task_type}'

    class Meta:
        indexes = [
            models.Index(fields=['task_employee_user']),
            models.Index(fields=['check_out_user']),
            models.Index(fields=['project_task_name']),
            models.Index(fields=['task_status']),
            models.Index(fields=['task_type']),
            models.Index(fields=['task_type_group']),
            models.Index(fields=['stock_active']),
            models.Index(fields=['project_teg']),
        ]


@receiver(pre_save, sender=Task)
def update_checked_time(sender, instance, **kwargs):
    if instance.pk is not None:
        original_task = Task.objects.get(pk=instance.pk)

        if original_task.task_status != instance.task_status:
            if instance.task_status == 'checked':
                instance.checked_time = timezone.now()
            elif instance.task_status == 'in progress' and not instance.in_progress_time:
                instance.in_progress_time = timezone.now()
            elif instance.task_status == 'complete':
                instance.complete_time = timezone.now()
        if original_task.task_status == 'complete' and instance.task_status == 'correcting':
            instance.total_correcting = original_task.total_correcting + 1

        if original_task.stock_active != instance.stock_active and instance.stock_active:
            instance.in_stock_active = timezone.now()


class Region(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


#   03.01.2024
class StorageStatus(models.Model):
    before_status = models.CharField(max_length=20, choices=STATUS)
    after_status = models.CharField(max_length=20, choices=STATUS)
    update_user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='StorageStatus',
    )
    create_data = models.DateTimeField(auto_now_add=True)
    storage_task = models.ForeignKey(
        "Task",
        on_delete=models.CASCADE,
        related_name="StorageStatus",
        blank=True,
        null=True
    )


class MessageImage(models.Model):
    img = models.ImageField(upload_to=message_image, null=True, blank=True)


class TaskMessage(models.Model):
    user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='TaskMessageUser',
    )
    task_id = models.ForeignKey(
        "Task",
        on_delete=models.CASCADE,
        related_name="TaskMessageTask",
    )
    message = models.CharField(max_length=1024, null=True, blank=True)
    message_image = models.ManyToManyField(MessageImage, blank=True)
    create_data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.task_id.project_name}({self.task_id.type}) -> {self.user.username}'

