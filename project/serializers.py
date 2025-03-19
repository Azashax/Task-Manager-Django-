from rest_framework import serializers
import User.views
from .models import Project, Task, Region, StorageStatus, TaskMessage, ProjectsFilterTeg
from User.serializers import UserSerializer
from User.models import MyUser

#     ________________________Filter teg_________________________


class ProjectsFilterTegSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectsFilterTeg
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    task_employee_user = UserSerializer()

    class Meta:
        model = Task
        fields = '__all__'


class TaskCompleteCheckOutSerializer(serializers.ModelSerializer):
    task_employee_user = UserSerializer()
    check_out_user = UserSerializer()

    class Meta:
        model = Task
        fields = '__all__'


class TaskInProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'project_task_name', 'project_id', 'task_status', 'task_type', 'time_point', 'point', 'task_employee_user',
                  'stock_active', 'in_stock_active', 'description']


class Task1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['project_type', 'project_name', 'built', 'link_clickup', 'link_cet3', 'region', 'filter_teg']
        ref_name = 'Project_add'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name']


class ProjectlistSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = Project
        fields = '__all__'
        ref_name = 'Projects'


class ProjectListGetSerializer(serializers.ModelSerializer):
    region = RegionSerializer()
    project_teamlead_user = UserSerializer()

    class Meta:
        model = Project
        fields = '__all__'
        ref_name = 'Projects'


class ProjectEmployeeSerializer(serializers.ModelSerializer):
    task_with = TaskInProgressSerializer()
    task_without = TaskInProgressSerializer()
    task_assemble = TaskInProgressSerializer()
    task_gltf = TaskInProgressSerializer()
    task_upload = TaskInProgressSerializer()
    task_render2d = TaskInProgressSerializer()
    task_render2d_upload = TaskInProgressSerializer()
    task_render3d = TaskInProgressSerializer()
    region = RegionSerializer()
    project_teamlead_user = UserSerializer()

    class Meta:
        model = Project
        fields = '__all__'
        ref_name = 'Project'


class UserDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'first_name', 'last_name']
        ref_name = 'DjoserUser3'


class TaskDashboardSerializer(serializers.ModelSerializer):
    task_employee_user = UserDashboardSerializer()

    class Meta:
        model = Task
        fields = ['id', 'task_status', 'task_type', 'task_employee_user']


class ProjectDashboardSerializer(serializers.ModelSerializer):
    task_with = TaskDashboardSerializer()
    task_without = TaskDashboardSerializer()
    task_assemble = TaskDashboardSerializer()
    task_gltf = TaskDashboardSerializer()
    task_upload = TaskDashboardSerializer()
    task_render2d = TaskDashboardSerializer()
    task_render2d_upload = TaskDashboardSerializer()
    task_render3d = TaskDashboardSerializer()
    filter_teg = ProjectsFilterTegSerializer()

    class Meta:
        model = Project
        exclude = ['description', 'link_cet3', 'link_clickup']


class ProjectDetailUpdateSerializer1(serializers.ModelSerializer):
    region = RegionSerializer()
    project_teamlead_user = UserSerializer()
    filter_teg = ProjectsFilterTegSerializer()

    class Meta:
        model = Project
        fields = '__all__'
        ref_name = 'Project'


class RegionSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class ProjectDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        ref_name = 'Project'


def create_or_update_task(self, instance, task_data, task_type):
    task_instance, created = Task.objects.get_or_create(project=instance, task_type=task_type)
    task_serializer = TaskSerializer(instance=task_instance, data=task_data)
    if task_serializer.is_valid():
        task_serializer.save()


class ProjectSerializer(serializers.ModelSerializer):
    task_with = TaskCompleteCheckOutSerializer()
    task_without = TaskCompleteCheckOutSerializer()
    task_assemble = TaskCompleteCheckOutSerializer()
    task_gltf = TaskCompleteCheckOutSerializer()
    task_upload = TaskCompleteCheckOutSerializer()
    task_render2d = TaskCompleteCheckOutSerializer()
    task_render3d = TaskCompleteCheckOutSerializer()
    task_render2d_upload = TaskCompleteCheckOutSerializer()
    filter_teg = ProjectsFilterTegSerializer()
    region = RegionSerializer()
    project_teamlead_user = UserSerializer()

    class Meta:
        model = Project
        fields = '__all__'
        ref_name = 'Project'

    def create(self, validated_data):
        project = Project.objects.create(**validated_data)

        # Создание или обновление задач для всех типов
        for task_type in ['with', 'without', 'assemble', 'gltf', 'upload', 'render2d', 'render2d_upload', 'render3d']:
            task_data = validated_data.pop(f'task_{task_type}', {})
            self.create_or_update_task(project, task_data, task_type)

        project.save()
        return project

    def update(self, instance, validated_data):
        instance = super(ProjectSerializer, self).update(instance, validated_data)

        # Создание или обновление задач для всех типов
        for task_type in ['with', 'without', 'assemble', 'gltf', 'upload', 'render2d', 'render2d_upload', 'render3d']:
            task_data = validated_data.pop(f'task_{task_type}', {})
            self.create_or_update_task(instance, task_data, task_type)

        instance.save()
        return instance


#   03.01.2024
class StorageSerializer(serializers.ModelSerializer):
    storage_task = Task1Serializer()
    update_user = UserSerializer()

    class Meta:
        model = StorageStatus
        fields = '__all__'


class StoragePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageStatus
        fields = '__all__'


class TaskMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskMessage
        fields = '__all__'


class TasksCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TasksListSerializer(serializers.ModelSerializer):
    task_employee_user = UserSerializer()
    check_out_user = UserSerializer()

    class Meta:
        model = Task
        fields = '__all__'
