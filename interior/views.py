from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from .paginations import PaginationProjects
from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework import generics, viewsets, mixins, status
from User.serializers import UserSerializer
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from User.models import Teams, MyUser
from rest_framework.exceptions import NotFound
from django.utils.dateparse import parse_datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from datetime import datetime


class DashboardAPIList(generics.ListAPIView):
    serializer_class = DashboardProjectSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = PaginationProjects

    def get_queryset(self):
        # Базовый запрос с выбором только нужных полей
        queryset = Project.objects.only('id', 'title', 'filter_teg', 'region', 'tasks').select_related('filter_teg', 'region')

        # Фильтрация по региону, если передан параметр region
        region_name = self.request.query_params.get('region')
        if region_name:
            queryset = queryset.filter(region__name=region_name)

        # Фильтрация по тегу, если передан параметр filter_teg
        filter_teg = self.request.query_params.get('filter_teg')
        if filter_teg:
            queryset = queryset.filter(filter_teg__teg=filter_teg)

        # Поиск по title, если передан параметр search
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        type_query = self.request.query_params.get('task_type')
        if type_query:
            queryset = queryset.filter(task__type=type_query)

        status_query = self.request.query_params.get('task_status')
        if status_query:
            queryset = queryset.filter(task__status=status_query)

        # Используем prefetch_related для оптимизации запросов связанных задач
        queryset = queryset.prefetch_related(
            Prefetch('tasks', queryset=Task.objects.only('id', 'type', 'status'))
        )

        return queryset.order_by('id')


def aggregate_task_status_counts(task_type):
    return {
        'open': Task.objects.filter(type=task_type, task_status='open').count(),
        'in_progress': Task.objects.filter(type=task_type, task_status='in progress').count(),
        'waiting': Task.objects.filter(type=task_type, task_status='waiting').count(),
        'complete': Task.objects.filter(type=task_type, task_status='complete').count(),
        'checked': Task.objects.filter(type=task_type, task_status='checked').count(),
        'correcting': Task.objects.filter(type=task_type, task_status='correcting').count(),
    }


class DashboardStatusAPIList(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, **kwargs):
        task_status_summary = {
            # 'project_status_count': aggregate_project_status_counts('project_status'),
            # 'exterior_status_count': aggregate_project_status_counts('exterior_status'),
            'task_assemble_status_counts': aggregate_task_status_counts('assemble'),
            'task_with_status_counts': aggregate_task_status_counts('with'),
            'task_without_status_counts': aggregate_task_status_counts('without'),
            'task_gltf_status_counts': aggregate_task_status_counts('gltf'),
            'task_upload_status_counts': aggregate_task_status_counts('upload'),
            'task_render2d_status_counts': aggregate_task_status_counts('render2d'),
            'task_render2d_upload_status_counts': aggregate_task_status_counts('render2d_upload'),
            'task_render3d_status_counts': aggregate_task_status_counts('render3d'),
        }

        return Response(task_status_summary, status=status.HTTP_200_OK)


class UpdateTaskPositions(APIView):
    """
    Представление для обновления позиций задач
    """

    def patch(self, request):
        tasks_data = request.data.get('tasks', None)
        if not tasks_data:
            return Response({'error': 'Tasks data is required'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TaskPositionSerializer(data=tasks_data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        task_ids = [task['id'] for task in validated_data]

        # Получаем все объекты UserTaskStock сразу, чтобы минимизировать запросы
        tasks_to_update = UserTaskStock.objects.filter(task_id__in=task_ids).select_related('task')
        tasks_map = {task.task_id: task for task in tasks_to_update}

        tasks_to_save = []
        tasks_to_update_status = []

        with transaction.atomic():
            for task_data in validated_data:
                task_id = task_data['id']
                new_position = task_data['position']

                task = tasks_map.get(task_id)
                if not task:
                    return Response({'error': f'Task with id {task_id} not found'}, status=status.HTTP_404_NOT_FOUND)

                task.position = new_position

                # Проверяем и обновляем статус задачи
                if new_position != 1 and task.task.status == 'in progress':
                    task.task.status = 'waiting'
                    tasks_to_update_status.append(task.task)

                tasks_to_save.append(task)

            # Массовое обновление UserTaskStock
            UserTaskStock.objects.bulk_update(tasks_to_save, ['position'])

            # Массовое обновление статусов Task
            if tasks_to_update_status:
                Task.objects.bulk_update(tasks_to_update_status, ['status'])

        return Response({'detail': 'Positions updated successfully'}, status=status.HTTP_200_OK)


class UnassignedTaskAPIList(generics.ListAPIView):
    queryset = UnassignedTasks.objects.all()
    serializer_class = UnassignedTasksSerializer
    permission_classes = (IsAuthenticated, )


# class TeamEmployeesTaskAPIList(generics.ListAPIView):
#     queryset = UserTaskStock.objects.all()
#     serializer_class = UserTaskStockSerializer
#     permission_classes = (IsAuthenticated, )


class TasksForReviewAPIList(generics.ListAPIView):
    queryset = TaskForReview.objects.all()
    serializer_class = TaskForReviewSerializer
    permission_classes = (IsAuthenticated, )


class EmployeeAPIList(generics.ListAPIView):
    queryset = MyUser.objects.filter(role="InteriorEmployee")
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )


class TeamLeadAPIList(generics.ListAPIView):
    queryset = MyUser.objects.filter(role="InteriorTeamLead")
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )


class EmployeeTasksAPIList(generics.ListCreateAPIView):
    serializer_class = UserTaskStockSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        queryset = UserTaskStock.objects.all()

        # Проверяем роль пользователя
        if self.request.user.role == "InteriorEmployee":
            # Фильтруем задачи, связанные с данным пользователем и позицией
            print(self.request.user)
            queryset = queryset.filter(task__employee_user=self.request.user.id)

            # Фильтруем задачу с позицией 1
            task_active = queryset.filter(position=1).first()  # Получаем единственный объект
            # Обновляем статус задачи, если он не "in progress"
            if task_active and task_active.task.status != "in progress":
                task_active.task.status = "in progress"
                task_active.task.save()

        return queryset


class TeamEmployeesTaskAPIList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        try:
            team = Teams.objects.get(teamlead=user)
        except Teams.DoesNotExist:
            raise NotFound("У вас нет группы")

        # Получаем участников команды и задачи для каждого
        team_members = team.employees.all()
        tasks = UserTaskStock.objects.filter(task__employee_user__in=team_members)

        # Сериализуем участников команды
        team_members_serializer = UserSerializer(team_members, many=True)

        # Сериализуем задачи, связанные с командой
        tasks_serializer = UserTaskStockSerializer(tasks, many=True)
        # Возвращаем структурированный ответ
        return Response({
            'users': team_members_serializer.data,
            'tasks': tasks_serializer.data
        }, status=status.HTTP_200_OK)


class StockAPIDetailUpdate(generics.RetrieveUpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated, )


class ProjectAPIListCreate(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = PaginationProjects


class ProjectAPIDetailUpdate(generics.RetrieveUpdateAPIView):
    queryset = Project.objects.all()
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        # Для GET-запросов используем сериализатор для чтения данных
        if self.request.method == 'GET':
            return ProjectDetailsSerializer
        # Для PATCH/POST-запросов используем сериализатор для записи данных
        return ProjectDetailsWriteSerializer


class ProjectTasksAPIListCreate(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = ProjectTasksSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        project_pk = self.kwargs.get('pk')
        return Task.objects.filter(project__id=project_pk).select_related('project')


class RegionAPIListCreate(generics.ListCreateAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = (IsAuthenticated, )


class RegionAPIDetailUpdate(generics.RetrieveUpdateAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = (IsAuthenticated, )


class TaskAPIListCreate(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, )

    def perform_create(self, serializer):
        serializer.save(changed_by=self.request.user)


class TaskAPIDetailUpdate(generics.RetrieveUpdateAPIView):
    queryset = Task.objects.all()
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        # Для GET-запросов используем сериализатор для чтения данных
        if self.request.method == 'GET':
            return TaskWithDetailsSerializer
        # Для PATCH/POST-запросов используем сериализатор для записи данных
        return TaskSerializer

    def perform_update(self, serializer):
        serializer.save(changed_by=self.request.user)


class ProjectsFilterTegAPIListCreate(generics.ListCreateAPIView):
    queryset = ProjectsFilterTeg.objects.all()
    serializer_class = ProjectsFilterTegSerializer
    permission_classes = (IsAuthenticated, )


class ProjectsFilterTegAPIDetailUpdate(generics.RetrieveUpdateAPIView):
    queryset = ProjectsFilterTeg.objects.all()
    serializer_class = ProjectsFilterTegSerializer
    permission_classes = (IsAuthenticated, )


class TaskImagesAPIListCreate(generics.ListCreateAPIView):
    queryset = TaskImages.objects.all()
    serializer_class = TaskImagesSerializer
    permission_classes = (IsAuthenticated, )


class TaskImagesAPIDetailUpdate(generics.RetrieveUpdateAPIView):
    queryset = TaskImages.objects.all()
    serializer_class = TaskImagesSerializer
    permission_classes = (IsAuthenticated, )


class TaskFilesAPIListCreate(generics.ListCreateAPIView):
    queryset = TaskFiles.objects.all()
    serializer_class = TaskImagesSerializer
    permission_classes = (IsAuthenticated, )


class TaskFilesAPIDetailUpdate(generics.RetrieveUpdateAPIView):
    queryset = TaskFiles.objects.all()
    serializer_class = TaskImagesSerializer
    permission_classes = (IsAuthenticated, )


class TaskMessageListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        task_id = self.kwargs['pk']
        return TaskMessage.objects.filter(task=task_id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskMessageCreateSerializer  # Используем этот сериализатор для создания
        return TaskMessageSerializer  # Используем этот сериализатор для получения

    def perform_create(self, serializer):
        task_id = self.kwargs['pk']
        task_instance = get_object_or_404(Task, pk=task_id)
        images_data = self.request.FILES.getlist('images')
        print(self.request.data)
        if not images_data and not self.request.data.get("message", "").strip():
            raise ValidationError("Message or at least one image is required")

        with transaction.atomic():
            # Сохраняем TaskMessage без изображений
            task_message = serializer.save(
                task=task_instance,
                number_correcting=task_instance.total_correcting,
                message=self.request.data.get("message", ""),
                user=self.request.user
            )

            # Добавляем изображения
            for image_data in images_data:
                try:
                    MessageImage.objects.create(task_message=task_message, img=image_data)
                except Exception as e:
                    print(f"Error saving image {image_data}: {e}")

            print(f"TaskMessage created for Task ID {task_id} with {len(images_data)} images.")


class RatingTasksAPIView(APIView):
    def get(self, request):
        # Получаем параметры start_date и end_date из запроса
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        # Определяем временные рамки: текущий месяц по умолчанию или переданные параметры
        try:
            now = timezone.now()
            start_date = (
                parse_datetime(start_date_str) if start_date_str else now.replace(day=1)
            )
            end_date = (
                parse_datetime(end_date_str) if end_date_str else (start_date + relativedelta(
                    months=1)) - relativedelta(days=1)
            )
            if timezone.is_naive(start_date):
                start_date = timezone.make_aware(start_date)
            if timezone.is_naive(end_date):
                end_date = timezone.make_aware(end_date)
            if not start_date or not end_date:
                raise ValidationError("Параметры start_date и end_date обязательны.")
        except (ValueError, TypeError):
            raise ValidationError("Некорректный формат даты. Используйте формат ISO 8601.")

        # Фильтруем активных сотрудников с ролью "InteriorEmployee"
        employee_users = MyUser.objects.filter(
            role="InteriorEmployee", is_active=True
        ).prefetch_related(
            Prefetch(
                "tasks_as_employee",  # Замените на точное имя обратной связи
                queryset=Task.objects.filter(
                    status="checked",
                    checked_time__gte=start_date,
                    checked_time__lte=end_date,
                ).select_related("project"),
                to_attr="filtered_tasks"
            )
        )

        # Формируем ответ с группировкой задач по сотрудникам
        response_data = [
            {
                "employee_name": {
                    'id': employee.id,
                    'first_name': employee.first_name,
                    'last_name': employee.last_name,
                },
                "tasks": [
                    {
                        "id": task.id,
                        "type": task.type,
                        "project": task.project.title,
                        "project_id": task.project.id,
                        "point": task.point,
                        "additional_point": task.additional_point,
                        "total_correcting": task.total_correcting,
                    }
                    for task in getattr(employee, 'filtered_tasks', [])
                ],
            }
            for employee in employee_users
        ]

        # Проверка, найдены ли задачи
        if not response_data:
            return Response({"detail": "Задачи не найдены."}, status=status.HTTP_404_NOT_FOUND)

        print(response_data)
        return Response(response_data, status=status.HTTP_200_OK)


class ProfileAPIDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskInProgressAPIUpdate(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, task_id):
        # Получаем задачу, или возвращаем 404, если не существует
        task = get_object_or_404(Task, id=task_id)

        # Проверяем, есть ли файл в запросе
        file = request.FILES.get('file')
        if file:
            # Создаем запись о файле
            TaskFiles.objects.create(task=task, file=file)

        # Проверяем, есть ли статус в запросе
        status_value = request.data.get("status")
        if not status_value:
            return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Обновляем статус задачи
        task.status = status_value
        task.save()

        # Сериализуем обновленный объект
        serializer = TaskSerializer(task)

        return Response(serializer.data, status=status.HTTP_200_OK)

