from rest_framework import serializers
from .models import (
    Project, Region, Task, ProjectsFilterTeg,
    TaskImages, TaskFiles, UserTaskStock, UnassignedTasks,
    TaskForReview, TaskMessage, MessageImage
)
from User.serializers import UserSerializer


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class ProjectsFilterTegSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectsFilterTeg
        fields = '__all__'


class TaskImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskImages
        fields = '__all__'


class TaskFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskFiles
        fields = '__all__'


class MessageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageImage
        fields = ['id', 'img']


class TaskMessageSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    task_message_images = MessageImageSerializer(many=True, read_only=True)  # Добавлено `many=True` и `read_only=True`

    class Meta:
        model = TaskMessage
        fields = ['id', 'user', 'task', 'message', 'task_message_images', 'create_at', 'update_at']


class TaskMessageCreateSerializer(serializers.ModelSerializer):
    task_message_images = MessageImageSerializer(many=True, read_only=True)  # Добавлено `many=True` и `read_only=True`

    class Meta:
        model = TaskMessage
        fields = ['id', 'user', 'task', 'message', 'task_message_images', 'create_at', 'update_at']


class DashboardTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'type', 'status']


class DashboardProjectSerializer(serializers.ModelSerializer):
    tasks = DashboardTaskSerializer(many=True, read_only=True)
    filter_teg = ProjectsFilterTegSerializer()

    class Meta:
        model = Project
        fields = ['id', 'title', 'tasks', 'status', 'region', 'filter_teg']


class ProjectTasksSerializer(serializers.ModelSerializer):
    qa_user = UserSerializer()
    employee_user = UserSerializer()

    class Meta:
        model = Task
        fields = '__all__'


class ProjectDetailsSerializer(serializers.ModelSerializer):
    team_lead_user = UserSerializer()  # Вложенный сериализатор для получения полной информации о пользователе
    filter_teg = ProjectsFilterTegSerializer()  # Вложенный сериализатор для тега
    region = RegionSerializer()  # Вложенный сериализатор для региона

    class Meta:
        model = Project
        fields = '__all__'


class ProjectDetailsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class TaskWithDetailsSerializer(serializers.ModelSerializer):
    qa_user = UserSerializer()
    employee_user = UserSerializer()

    class Meta:
        model = Task
        fields = '__all__'


class TaskDetailsSerializer(serializers.ModelSerializer):
    qa_user = UserSerializer()
    employee_user = UserSerializer()
    project = ProjectSerializer()

    class Meta:
        model = Task
        fields = '__all__'


class TaskForReviewSerializer(serializers.ModelSerializer):
    task = TaskDetailsSerializer()

    class Meta:
        model = TaskForReview
        fields = '__all__'


class UnassignedTasksSerializer(serializers.ModelSerializer):
    task = TaskDetailsSerializer()

    class Meta:
        model = UnassignedTasks
        fields = '__all__'


class UserTaskStockSerializer(serializers.ModelSerializer):
    task = TaskDetailsSerializer()

    class Meta:
        model = UserTaskStock
        fields = '__all__'


class TaskPositionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    position = serializers.IntegerField()