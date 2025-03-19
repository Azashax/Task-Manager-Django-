from django.db import models
from User.models import MyUser
from project.models import STATUS, TEG, Region
from .utils_upload import *
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

PROJECT_EX_TYPE = (
    ('Stab', 'Stab'),
    ('OffPlan', 'OffPlan'),
    ('tower', 'tower'),
)


OBJECTS_EX_TYPE = (
    ('BuildDetails', 'BuildDetails'),
    ('Floor', 'Floor'),
    ('Objects', 'Objects'),
    ('StaticObject', 'StaticObject'),
)


class ProjectExterior(models.Model):
    project_type = models.CharField(max_length=20, choices=PROJECT_EX_TYPE, default=PROJECT_EX_TYPE[0][0])
    project_ex_teamlead_user = models.ForeignKey(
        MyUser,
        verbose_name='EX Тимлид',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ExTeamlead'},
        related_name='ex_teamlead_projects',
        null=True,
        blank=True
    )
    project_ex_employee_user = models.ForeignKey(
        MyUser,
        verbose_name='EX Employee',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ExEmployee'},
        related_name='ex_employee_projects',
        null=True,
        blank=True
    )
    project_name = models.CharField(max_length=255)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="exterior_projects", blank=True, null=True)
    link_clickup = models.TextField(blank=True, null=True)
    link_cet3 = models.TextField(blank=True, null=True)
    project_teg = models.CharField(max_length=20, choices=TEG, default=TEG[0][0])
    exterior_status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0][0])
    description = models.TextField(blank=True, null=True)
    texture = models.FileField(upload_to=project_texture, validators=[validate_file_extension], null=True, blank=True)

    finished_point_low = models.CharField(max_length=255, blank=True, null=True)
    finished_point_high = models.CharField(max_length=255, blank=True, null=True)
    finished_point_midl = models.CharField(max_length=255, blank=True, null=True)

    finished_time_low = models.CharField(max_length=255, blank=True, null=True)
    finished_time_high = models.CharField(max_length=255, blank=True, null=True)
    finished_time_midl = models.CharField(max_length=255, blank=True, null=True)    # default="0d 0h 0m 0s",
    create_data = models.DateTimeField(auto_now_add=True)
    quantity_correcting = models.IntegerField(default=0)
    serial_number = models.IntegerField(default=0)
    in_stock_active = models.DateTimeField(null=True, blank=True)
    stock_active = models.BooleanField(default=False)

    calculated = models.BooleanField(default=False)

    def __str__(self):
        return self.project_name


class ExteriorTask(models.Model):
    TASK_TYPE = (
        ('Low Poly', 'Low Poly'),
        ('Midl Poly', 'Midl Poly'),
        ('High Poly', 'High Poly'),
        ('Arrangement', 'Arrangement'),
    )
    task_employee_user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь Employee',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ExEmployee'},
        related_name='Ex_task_employee_user',
        null=True,
        blank=True
    )
    check_out_user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь Qa',
        on_delete=models.CASCADE,
        related_name='Ex_task_qa_user',
        null=True,
        blank=True
    )
    check_out = models.BooleanField(default=False)
    project_exterior_id = models.ForeignKey(ProjectExterior, on_delete=models.CASCADE, related_name="ExteriorTask")
    task_status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0][0])
    task_type = models.CharField(max_length=20, choices=TASK_TYPE, default=TASK_TYPE[0][0])
    project_teg = models.CharField(max_length=20, choices=TEG, default="None")
    in_progress_time = models.DateTimeField(null=True, blank=True)
    in_stock_active = models.DateTimeField(null=True, blank=True)
    checked_time = models.DateTimeField(null=True, blank=True)
    complete_time = models.DateTimeField(null=True, blank=True)
    point = models.FloatField(null=True, blank=True)
    time_point = models.CharField(max_length=100, null=True, blank=True)
    total_correcting = models.IntegerField(default=0)
    stock_active = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.project_exterior_id} -> {self.task_type}'


@receiver(pre_save, sender=ExteriorTask)
def update_checked_time(sender, instance, **kwargs):
    if instance.pk is not None:
        original_task = ExteriorTask.objects.get(pk=instance.pk)

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


class ExteriorStorageStatus(models.Model):
    before_status = models.CharField(max_length=20, choices=STATUS)
    after_status = models.CharField(max_length=20, choices=STATUS)
    update_user = models.ForeignKey(
        MyUser,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='ExteriorStorageStatus',)
    storage_task = models.ForeignKey(
        ExteriorTask,
        on_delete=models.CASCADE,
        related_name="ExteriorStorageStatus",
        blank=True,
        null=True)
    create_data = models.DateTimeField(auto_now_add=True)


'''   ----------------------------------------------- Калькулятор ------------------------------------------------   '''


class ProjectsImage(models.Model):
    img = models.ImageField(upload_to=screenshots, null=True, blank=True)


class Building(models.Model):
    title = models.CharField(max_length=100)
    project_exterior = models.ForeignKey(ProjectExterior, on_delete=models.CASCADE, related_name="buildings")

    mid_poly = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    copy_count = models.IntegerField(default=0)
    finished_point = models.CharField(max_length=255, blank=True, null=True)
    finished_time = models.CharField(max_length=255, blank=True, null=True)

    screenshots = models.ManyToManyField(ProjectsImage, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} (ID: {self.id})'


class TopologyHard(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    data = models.JSONField(null=True, blank=True, default=dict)
    screenshots = models.ManyToManyField(ProjectsImage, blank=True)

    def __str__(self):
        return f'{self.title} (ID: {self.id})'


class BuildingObjects(models.Model):
    title = models.CharField(max_length=100)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="building_objects")
    objects_type = models.CharField(max_length=30, choices=OBJECTS_EX_TYPE)
    topology_hard = models.ManyToManyField(TopologyHard, blank=True)
    description = models.TextField(blank=True, null=True)
    data = models.JSONField(null=True, blank=True, default=dict)
    screenshots = models.ManyToManyField(ProjectsImage, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} (ID: {self.id})'


class Floors(models.Model):
    title = models.CharField(max_length=100)
    building_object = models.ForeignKey(BuildingObjects, on_delete=models.CASCADE, related_name="floors")
    topology_hard = models.ManyToManyField(TopologyHard, blank=True)
    objects_type = models.CharField(max_length=30, choices=OBJECTS_EX_TYPE, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    data = models.JSONField(null=True, blank=True, default=dict)
    screenshots = models.ManyToManyField(ProjectsImage, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} (ID: {self.id})'


class Details(models.Model):
    title = models.CharField(max_length=100)
    floors = models.ForeignKey(Floors, on_delete=models.CASCADE, related_name="details")
    data = models.JSONField(null=True, blank=True, default=dict)
    objects_type = models.CharField(max_length=30, choices=OBJECTS_EX_TYPE, null=True, blank=True)
    topology_hard = models.ManyToManyField(TopologyHard, blank=True)
    screenshots = models.ManyToManyField(ProjectsImage, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} (ID: {self.id})'


class AdditionalStructure(models.Model):
    geometry_straight = models.IntegerField(null=True, blank=True)
    geometry_curve = models.IntegerField(null=True, blank=True)
    topology_cyclical = models.IntegerField(null=True, blank=True)
    topology_chaotic = models.IntegerField(null=True, blank=True)
    deformation_easy = models.IntegerField(null=True, blank=True)
    deformation_hard = models.IntegerField(null=True, blank=True)
    symmetry = models.IntegerField(null=True, blank=True)
    copy = models.IntegerField(null=True, blank=True)
    cyclic_copy = models.IntegerField(null=True, blank=True)

    arabian_logo = models.IntegerField(null=True, blank=True)
    logo = models.IntegerField(null=True, blank=True)
    primitive = models.IntegerField(null=True, blank=True)
    furniture = models.IntegerField(null=True, blank=True)
    railing = models.IntegerField(null=True, blank=True)
    railing_curve = models.IntegerField(null=True, blank=True)
    staircase_straight = models.IntegerField(null=True, blank=True)
    staircase_curves = models.IntegerField(null=True, blank=True)

    high_poly = models.FloatField(null=True, blank=True)
    low_poly = models.IntegerField(null=True, blank=True)
    study_info = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(AdditionalStructure, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "Additional Structure"
