from rest_framework import serializers
from .models import ProjectListing, RenderTask, SubTask, ProjectFile, RenderTaskImages, MessageTaskImages, \
    MessageRenderTask, RenderTaskStatusChange
from User.serializers import UserSerializer
from User.models import MyUser
from datetime import date

class RenderTaskMessageUserSerializer(serializers.ModelSerializer):
    render_task_user_message = UserSerializer()

    class Meta:
        model = MessageRenderTask
        fields = '__all__'


class RenderTaskMessageFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageRenderTask
        fields = '__all__'


class RenderTaskImagesMessageFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTaskImages
        fields = '__all__'


class RenderTaskImagesFullSerializer(serializers.ModelSerializer):
    task_images_messages = RenderTaskImagesMessageFullSerializer(many=True, read_only=True)

    class Meta:
        model = RenderTaskImages
        fields = '__all__'


class SubTaskSerializer(serializers.ModelSerializer):
    sub_task_employee_id = UserSerializer()

    class Meta:
        model = SubTask
        fields = '__all__'


class RenderTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = RenderTask
        fields = '__all__'


class ProjectFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectFile
        fields = '__all__'


class ProjectListingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectListing
        fields = '__all__'


class RenderTaskNotImageSerializer(serializers.ModelSerializer):
    sub_task = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = RenderTask
        fields = ["id", "new_task", "project_id", "sub_task"]


class ProjectListingCountTaskSerializer(serializers.ModelSerializer):
    total_tasks_render = serializers.IntegerField(read_only=True)
    complete_tasks_render = serializers.IntegerField(read_only=True)
    in_progress_tasks_render = serializers.IntegerField(read_only=True)
    correcting_tasks_render = serializers.IntegerField(read_only=True)
    checked_tasks_render = serializers.IntegerField(read_only=True)
    open_tasks_render = serializers.IntegerField(read_only=True)
    new_tasks_render = serializers.IntegerField(read_only=True)
    total_tasks = serializers.IntegerField(read_only=True)
    complete_tasks = serializers.IntegerField(read_only=True)
    in_progress_tasks = serializers.IntegerField(read_only=True)
    checked_tasks = serializers.IntegerField(read_only=True)
    open_tasks = serializers.IntegerField(read_only=True)
    new_tasks = serializers.IntegerField(read_only=True)
    correcting_tasks = serializers.IntegerField(read_only=True)
    # project_task = RenderTaskNotImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectListing
        fields = '__all__'


class FilteredSubTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubTask
        fields = '__all__'


class RenderTaskSubTaskSerializer(serializers.ModelSerializer):
    sub_task = SubTaskSerializer(many=True, read_only=True)
    images = RenderTaskImagesFullSerializer(many=True, read_only=True)
    task_qa_id = UserSerializer()
    class Meta:
        model = RenderTask
        fields = '__all__'

    def to_representation(self, instance):
        # Получаем представление объекта с использованием базового метода
        representation = super().to_representation(instance)

        # Сортируем task_images по id
        if 'images' in representation:
            representation['images'] = sorted(representation['images'], key=lambda x: x['id'])

        return representation


class ProjectListingRenderTaskSubTaskSerializer(serializers.ModelSerializer):
    project_file = ProjectFileSerializer(many=True, read_only=True)
    project_task = RenderTaskSubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectListing
        fields = '__all__'


# class RenderTaskImagesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RenderTaskImages
#         fields = ('floor_plan_image', 'task_id', 'create_at')
#         extra_kwargs = {
#             'task_id': {'required': False}
#         }
#
#     def create(self, validated_data):
#         task_id = self.context['task_id']
#         task = RenderTask.objects.get(pk=task_id)
#         validated_data['task_id'] = task
#         return super().create(validated_data)


class RenderTaskImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenderTaskImages
        fields = '__all__'

    def create(self, validated_data):
        task_id = self.context.get('task_id')
        task = RenderTask.objects.get(id=task_id)
        render_task_image = RenderTaskImages.objects.create(**validated_data)
        task.images.add(render_task_image)
        return render_task_image

# class ProjectListingPerformanceSerializer(serializers.ModelSerializer):
#     tasks_count = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ProjectListing
#         fields = ['id', 'title', 'tasks_count']
#
#     def get_tasks_count(self, obj):
#         today = date.today()
#         return obj.project_task.filter(time_checked__date=today).count()
#
# class UserPerformanceSerializer(serializers.ModelSerializer):
#     project_count = serializers.SerializerMethodField()
#     task_count = serializers.SerializerMethodField()
#     projects_info = serializers.SerializerMethodField()
#
#     class Meta:
#         model = MyUser
#         fields = [
#             'user_full_name',
#             'project_count',
#             'task_count',
#             'projects_info'
#         ]
#
#     user_full_name = serializers.SerializerMethodField()
#
#     def get_user_full_name(self, obj):
#         return f"{obj.first_name} {obj.last_name}"
#
#     def get_project_count(self, obj):
#         today = date.today()
#         return ProjectListing.objects.filter(
#             project_task__task_employee_id=obj,
#             project_task__time_checked__date=today
#         ).distinct().count()
#
#
#     def get_task_count(self, obj):
#         today = date.today()
#         return RenderTask.objects.filter(
#             task_employee_id=obj,
#             time_checked__date=today
#         ).count()
#
#
#     def get_projects_info(self, obj):
#         today = date.today()
#         projects = ProjectListing.objects.filter(
#             project_task__task_employee_id=obj,
#             project_task__time_checked__date=today
#         ).distinct()
#         return ProjectListingPerformanceSerializer(projects, many=True).data


class ProjectListingPerformanceSerializer(serializers.ModelSerializer):
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = ProjectListing
        fields = ['id', 'title', 'tasks_count']

    def get_tasks_count(self, obj):
        start_date = self.context.get('start_date', date.today())
        end_date = self.context.get('end_date', date.today())
        return obj.project_task.filter(time_checked__date__range=(start_date, end_date)).count()


class UserPerformanceSerializer(serializers.ModelSerializer):
    checked_project_count = serializers.SerializerMethodField()
    checked_task_count = serializers.SerializerMethodField()
    complete_project_count = serializers.SerializerMethodField()
    complete_task_count = serializers.SerializerMethodField()
    # unique_complete_task_count = serializers.SerializerMethodField()
    total_complete_task_count = serializers.SerializerMethodField()
    projects_info = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = [
            'user_full_name',
            'checked_project_count',
            'checked_task_count',
            'complete_project_count',
            'complete_task_count',
            # 'unique_complete_task_count',
            'total_complete_task_count',
            'projects_info'
        ]

    user_full_name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        enhancer = self.context.get('enhancer')
        # Удаляем поле projects_info, если enhancer == "all"
        if enhancer == "all":
            self.fields.pop('projects_info')

    def get_user_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_checked_project_count(self, obj):
        start_date = self.context['start_date']
        end_date = self.context['end_date']
        return ProjectListing.objects.filter(
            project_task__sub_task__sub_task_employee_id=obj,
            project_task__sub_task__status="checked",
            project_task__time_checked__date__range=(start_date, end_date)
        ).distinct().count()

    def get_checked_task_count(self, obj):
        start_date = self.context['start_date']
        end_date = self.context['end_date']
        return RenderTask.objects.filter(
            sub_task__sub_task_employee_id=obj,
            sub_task__status="checked",
            time_checked__date__range=(start_date, end_date)
        ).count()

    def get_complete_project_count(self, obj):
        start_date = self.context['start_date']
        end_date = self.context['end_date']
        return ProjectListing.objects.filter(
            project_task__sub_task__sub_task_employee_id=obj,
            project_task__time_complete__date__range=(start_date, end_date)
        ).distinct().count()

    def get_complete_task_count(self, obj):
        start_date = self.context['start_date']
        end_date = self.context['end_date']
        return RenderTask.objects.filter(
            sub_task__sub_task_employee_id=obj,
            time_complete__date__range=(start_date, end_date)
        ).count()

    # def get_unique_complete_task_count(self, obj):
    #     start_date = self.context['start_date']
    #     end_date = self.context['end_date']
    #
    #     status_changes = RenderTaskStatusChange.objects.filter(
    #         task__sub_task_employee_id=obj,
    #         new_status="complete",
    #         changed_at__date__range=(start_date, end_date)
    #     ).values('task_id').distinct()
    #     return status_changes.count()

    def get_total_complete_task_count(self, obj):
        start_date = self.context['start_date']
        end_date = self.context['end_date']
        print(RenderTaskStatusChange.objects.filter(
            changed_by=obj,
            new_status="complete",  # Статус "complete"
            changed_at__date__range=(start_date, end_date)
        ).count())
        return RenderTaskStatusChange.objects.filter(
            changed_by=obj,
            new_status="complete",  # Статус "complete"
            changed_at__date__range=(start_date, end_date)
        ).count()

    def get_projects_info(self, obj):
        start_date = self.context['start_date']
        end_date = self.context['end_date']
        projects = ProjectListing.objects.filter(
            project_task__sub_task__sub_task_employee_id=obj,
            project_task__time_checked__date__range=(start_date, end_date)
        ).distinct()
        return ProjectListingPerformanceSerializer(projects, many=True, context={'start_date': start_date, 'end_date': end_date}).data


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'first_name', 'last_name',)
        ref_name = 'DjoserUser'


class EnhancerTaskActiveSerializer(serializers.Serializer):
    enhancer_name = serializers.CharField()
    in_progress_count = serializers.IntegerField()
    complete_count = serializers.IntegerField()
