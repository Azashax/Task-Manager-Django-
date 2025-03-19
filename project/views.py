from rest_framework import generics, viewsets, mixins, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from task_manager.settings import TOKEN_TG_BOT, ID_USER
from .models import Project, Task, Region, StorageStatus, MessageImage
from .serializers import *
from .permissions import IsTeamlead, IsAdmin, IsAdminAndTeamlead, IsQAAndAdmin, ExceptEmployee, IsAdminAndManager
from django.db.models import Case, When, Value, CharField, Q, Max, F
from django.shortcuts import get_object_or_404
from User.models import Teams, MyUser
from rest_framework.exceptions import NotFound
from User.serializers import UserTeamSerializer, UserSerializer
from .paginations import PaginationProjects
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
import requests


class StockAPIUpdateEmployee(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        user = request.user
        if task.task_employee_user == user and task.stock_active:
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        serializer = TaskInProgressSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskCreateAPI(APIView):
    permission_classes = (IsAuthenticated, IsTeamlead)

    def post(self, request):
        # Создание сериализатора с переданными данными
        serializer = Task1Serializer(data=request.data)

        # Проверка валидности данных
        if serializer.is_valid():
            # Получение project_id из переданных данных
            project_id = serializer.validated_data.get('project_id')
            task_type = serializer.validated_data.get('task_type')
            try:
                # Поиск проекта с указанным project_id
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                # Если проект не найден, вернуть ошибку
                return Response({"error": "Project does not exist."}, status=status.HTTP_404_NOT_FOUND)

            # Создание задачи с переданными данными и связь с проектом через соответствующее поле
            task = Task.objects.create(
                task_type=serializer.validated_data['task_type'],
                project_task_name=serializer.validated_data['project_task_name'],
                project_id=project.id
            )

            # Связывание созданной задачи с полем project.task_render в проекте
            if task_type == "render3d":
                project.task_render3d = task
            elif task_type == "render2d":
                project.task_render2d = task
            else:
                project.task_render2d_upload = task
            project.save()

            # Возвращение успешного ответа с данными задачи
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Если данные не валидны, вернуть ошибку
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StockEmployeeAPIList(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user

        tasks = Task.objects.filter(
            time_point__isnull=False,
            point__isnull=False,
            stock_active=True,
            task_employee_user=user
        ).select_related('task_employee_user').order_by('in_stock_active')

        earliest_task = tasks.first()

        if earliest_task:
            earliest_task.task_status = 'in progress'
            earliest_task.save()

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SecureTeamleadUpdateAPI(APIView):
    permission_classes = (IsAuthenticated, IsTeamlead)

    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        serializer = Task1Serializer(task)
        return Response(serializer.data)

    def patch(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        # Преобразование 'task_employee_user' в число, если это строка
        task_employee_user = request.data.get('task_employee_user')
        if task_employee_user is not None and not isinstance(task_employee_user, int):
            try:
                task_employee_user = int(task_employee_user)
            except ValueError:
                return Response({"task_employee_user": "Некорректное значение"}, status=status.HTTP_400_BAD_REQUEST)
        request.data['task_employee_user'] = task_employee_user
        serializer = Task1Serializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if task.task_status == "in progress":
                user_id = serializer.validated_data.get('task_employee_user')
                if user_id is not None:
                    queryset = Task.objects.filter(
                        task_employee_user=user_id,
                        stock_active=True
                    ).only('in_stock_active').order_by('in_stock_active')
                    if queryset.exists():
                        task.stock_active = True
                        task.save()

            if task.task_status == "correcting":
                user_id = serializer.validated_data.get('task_employee_user')
                if user_id is not None:
                    queryset = Task.objects.filter(
                        task_employee_user=user_id,
                        stock_active=True
                    ).only('in_stock_active').order_by('in_stock_active')
                    if queryset.exists():
                        a = queryset.first()
                        b = queryset.filter(task_status="correcting").count()
                        new_in_stock_active = a.in_stock_active + timedelta(milliseconds=b + 1)
                        task.stock_active = True
                        task.save()
                        task.in_stock_active = new_in_stock_active
                        task.save()
                    else:
                        task.stock_active = True
                        task.save()
            if task.task_status == "waiting":
                user_id = serializer.validated_data.get('task_employee_user')
                if user_id is not None:
                    queryset = Task.objects.filter(
                        task_employee_user=user_id,
                        stock_active=True
                    ).only('in_stock_active').order_by('in_stock_active')
                    if queryset.exists():
                        a = queryset.first()
                        b = queryset.filter(task_status="correcting").count() or 0
                        new_in_stock_active = a.in_stock_active + timedelta(milliseconds=b + 1)
                        task.stock_active = True
                        task.save()
                        task.in_stock_active = new_in_stock_active
                        task.save()
                    else:
                        task.stock_active = True
                        task.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InProgressTeamleadAPIUpdate(APIView):
    permission_classes = (IsAuthenticated, IsTeamlead)

    def patch(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        task.status = 'waiting'
        task.save()
        serializer = TaskInProgressSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InProgressTeamleadAPIList(APIView):
    permission_classes = (IsAuthenticated, IsTeamlead)

    def get(self, request):
        user = request.user
        try:
            team = Teams.objects.get(teamlead=user)
        except Teams.DoesNotExist:
            raise NotFound("У вас нет группы")
        team_members = team.employees.values_list('id', flat=True)
        users = MyUser.objects.filter(id__in=team_members, is_active=True).order_by('username')
        user_serializer = UserSerializer(users, many=True)
        data = user_serializer.data
        for user_data in data:
            tasks = Task.objects.filter(
                task_employee_user=user_data['id'],
                time_point__isnull=False,
                point__isnull=False,
                stock_active=True,
                task_status__in=["open", "correcting", "waiting", "in progress"],
            ).order_by('in_stock_active')
            task_serializer = TaskInProgressSerializer(tasks, many=True)
            user_data['array'] = task_serializer.data
        return Response(data, status=status.HTTP_200_OK)


class SecureTeamleadAPIList(APIView):
    permission_classes = (IsAuthenticated, IsTeamlead)

    def get(self, request):
        user = request.user
        try:
            team = Teams.objects.get(teamlead=user)
        except Teams.DoesNotExist:
            raise NotFound("У вас нет группы")
        team_members = team.employees.values_list('id', flat=True)
        project_ids = Project.objects.all().values_list('id', flat=True)
        # .filter(
        #     project_teamlead_user=user
        # ).values_list('id', flat=True)
        projects1 = Task.objects.filter(
            time_point__isnull=False,
            point__isnull=False,
            stock_active=False,
            task_status__in=["open", "correcting", "waiting"],
            task_employee_user__in=team_members,
            project_id__in=[str(id) for id in project_ids]
        )
        projects = Task.objects.filter(
            time_point__isnull=False,
            point__isnull=False,
            stock_active=False,
            task_status="open",
            task_employee_user__isnull=True,
            project_id__in=[str(id) for id in project_ids])
        serializer1 = TaskSerializer(projects1, many=True)
        serializer = TaskSerializer(projects, many=True)
        team_members1 = MyUser.objects.filter(id__in=team_members, is_active=True)
        user_serializer = UserTeamSerializer(team_members1, many=True)
        data = {
            "tasks_open": serializer.data,
            "tasks": serializer1.data,
            "team_members": user_serializer.data
        }
        print(data)
        return Response(data, status=status.HTTP_200_OK)


class CompleteLoadAPIList(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        projects = Task.objects.filter(
                time_point__isnull=False,
                point__isnull=False,
                stock_active=False,
                task_status="complete",
                task_employee_user=user).order_by('complete_time')
        serializer = TaskCompleteCheckOutSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompleteAPIList(APIView):
    permission_classes = (IsAuthenticated, IsTeamlead)

    def get(self, request):
        user = request.user
        team = Teams.objects.filter(teamlead=user).first()
        if team:
            team_members = team.employees.values_list('id', flat=True)
            projects = Task.objects.filter(
                time_point__isnull=False,
                point__isnull=False,
                stock_active=False,
                task_status="complete",
                task_employee_user__in=team_members).order_by('complete_time')
            serializer = TaskCompleteCheckOutSerializer(projects, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("У вас нет Группы", status=status.HTTP_403_FORBIDDEN)


class CompleteUpdateAPIList(APIView):
    permission_classes = (IsAuthenticated, IsTeamlead)

    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk)  # Используйте get_object_or_404
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def patch(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if serializer.validated_data.get('task_status') == "correcting":
                user_id = serializer.data.get('task_employee_user')['id']
                queryset = Task.objects.filter(
                    task_employee_user=user_id,
                    stock_active=True
                ).only('in_stock_active').order_by('in_stock_active')
                a = queryset.first()

                b = queryset.filter(task_status="correcting").count()
                if queryset.exists():
                    new_in_stock_active = a.in_stock_active + timedelta(milliseconds=b+1)
                    task.stock_active = True
                    task.save()
                    task.in_stock_active = new_in_stock_active
                    task.save()
                else:
                    task.stock_active = True
                    task.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectAPIUpdate(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        project = get_object_or_404(Project, id=pk)  # Используйте get_object_or_404
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def patch(self, request, pk):
        project = get_object_or_404(Project, id=pk)
        for key in request.data.keys():
            parts = key.split("_")
            if len(parts) > 1:
                task_type = parts[1]
                if len(parts) > 2:
                    task_type += "_upload"
                task = Task.objects.get(project_task_name=project.project_name, task_type=task_type)
                serializer = Task1Serializer(task, data=request.data[key], partial=True)
                StorageStatus.objects.create(before_status="open",
                                             after_status="open",
                                             update_user=request.user,
                                             storage_task=task
                                             )
                a = {
                    "before_status": "open",
                    "after_status": "open",
                    "update_user": request.user,
                    "storage_task": task.id,
                }
                request_telegram_bot_team_lead(a, request.user.username)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response("Задачи успешно обновлены", status=status.HTTP_200_OK)


class ProjectDetailAPIUpdate(APIView):
    permission_classes = (IsAuthenticated, ExceptEmployee)

    def get(self, request, pk):
        project = get_object_or_404(Project, id=pk)
        serializer = ProjectDetailUpdateSerializer1(project)
        return Response(serializer.data)

    def patch(self, request, pk):
        project = get_object_or_404(Project, id=pk)
        serializer = ProjectDetailUpdateSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response("Проект успешно обновлен", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_project_filter(request, projects):
    search_query = request.query_params.get('project-name', None)
    if search_query:
        projects = projects.filter(
            Q(project_name__istartswith=search_query)
        )
    projects_p = projects.annotate(
        sorting_status=Case(
            When(project_teg='High priority', then=Value('A')),
            When(project_teg='Priority', then=Value('B')),
            default=Value('C'),
            output_field=CharField(),
        ),
    ).order_by('sorting_status')
    serializer = ProjectlistSerializer(projects_p, many=True)
    return Response(serializer.data)


class ProjectAPIList(generics.ListAPIView):
    """Output list of projects"""
    permission_classes = (IsAuthenticated, IsTeamlead)

    def get(self, request):
        projects = Project.objects.all()
        filter_t = request.query_params.get('filter_teg', None)
        search_query = request.query_params.get('search', '')
        if filter_t:
            projects = projects.filter(filter_teg__teg=filter_t)
        if search_query:
            projects = projects.filter(project_name__icontains=search_query)

        projects = projects.order_by('-id')
        serializer = ProjectlistSerializer(projects, many=True)
        return Response(serializer.data)


class ProjectTeamLeadAPIList(generics.ListAPIView):
    """Вывод списка проектов"""
    permission_classes = (IsAuthenticated, IsTeamlead)

    def get(self, request):
        projects = Project.objects.filter(project_teamlead_user=request.user)
        response = get_project_filter(request, projects)
        return response


class ProjectTeamLeadStockAPIList(generics.ListAPIView):
    """Вывод списка проектов"""
    permission_classes = (IsAuthenticated, IsTeamlead)

    def get(self, request):
        projects = Project.objects.filter(
            project_teamlead_user=request.user,
            task_without__task_status="checked",
            exterior_status="open"
        )
        response = get_project_filter(request, projects)
        return response


class RegionAPIList(APIView):
    permission_classes = (IsAuthenticated, IsAdminAndTeamlead)

    def get(self, request):
        regions = Region.objects.all()
        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RegionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectAPIListCreate(APIView):
    permission_classes = (IsAuthenticated, IsAdminAndTeamlead)

    def post(self, request):
        serializer = ProjectCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        projects = Project.objects.all()
        response = get_project_filter(request, projects)
        return response


class ProjectsStockAPIList(generics.ListAPIView):
    """Вывод списка проектов"""
    permission_classes = (IsAuthenticated, IsAdminAndManager)

    def get(self, request):
        projects = Project.objects.filter(
            task_without__task_status="checked",
            exterior_status="open"
        )
        response = get_project_filter(request, projects)
        return response

class DashboardAPIList(APIView):
    serializer_class = ProjectDashboardSerializer
    permission_classes = (IsAuthenticated, ExceptEmployee)
    pagination_class = PaginationProjects
    # filter_backends = [DjangoFilterBackend, SearchFilter]
    # search_fields = ['project_name', 'id']

    def get_queryset(self, request, *args, **kwargs):
        projects = Project.objects.all().prefetch_related(
            'task_with',
            'task_without',
            'task_assemble',
            'task_gltf',
            'task_upload',
            'task_render2d',
            'task_render2d_upload',
            'task_render3d'
        )
        print(projects)
        filter_t = request.query_params.get('filter_teg', None)
        search_query = request.GET.get('search', '')
        print(request.data)
        print(request.query_params)
        if filter_t:
            projects = projects.filter(filter_teg__teg=filter_t)
        if search_query:
            projects = projects.filter(project_name__icontains=search_query)
        return projects.order_by('-id')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request, *args, **kwargs)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(queryset, request)

        serializer = ProjectDashboardSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

# class DashboardAPIList(APIView):
#     permission_classes = (IsAuthenticated, ExceptEmployee)
#
#     def get(self, request, *args, **kwargs):
#         projects = Project.objects.all()
#         search_query = request.query_params.get('project-name', None)
#         if search_query:
#             projects = projects.filter(
#                 Q(project_name__istartswith=search_query)
#             )
#         serializer = ProjectDashboardSerializer(projects, many=True)
#         return Response(serializer.data)


class InProgressAllAPIList(APIView):
    permission_classes = (IsAuthenticated, IsAdminAndManager)

    def get(self, *args, **kwargs):
        users = MyUser.objects.filter(role="Employee", is_active=True).order_by('username')
        users_serializer = UserSerializer(users, many=True)
        data = users_serializer.data
        for user_data in data:
            tasks = Task.objects.filter(
                task_employee_user=user_data['id'],
                time_point__isnull=False,
                point__isnull=False,
                stock_active=True,
                task_status__in=["open", "correcting", "waiting", "in progress"],
            )
            tasks = tasks.annotate(
                sorting_status=Case(
                    When(task_status='in progress', then=Value('A')),
                    default=Value('B'),
                    output_field=CharField(),
                ),
            ).order_by('in_stock_active', 'sorting_status')
            task_serializer = TaskInProgressSerializer(tasks, many=True)
            user_data['array'] = task_serializer.data
        return Response(data, status=status.HTTP_200_OK)


class CompleteUpdateAPIListAll(APIView):
    permission_classes = (IsAuthenticated, IsQAAndAdmin)

    def patch(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if serializer.validated_data.get('task_status') == "correcting":
                user_id = serializer.data.get('task_employee_user')['id']
                queryset = Task.objects.filter(
                    task_employee_user=user_id,
                    stock_active=True
                ).only('in_stock_active').order_by('in_stock_active')
                a = queryset.first()
                b = queryset.filter(task_status="correcting").count()
                if queryset.exists():
                    new_in_stock_active = a.in_stock_active + timedelta(milliseconds=b+1)
                    task.stock_active = True
                    task.save()
                    task.in_stock_active = new_in_stock_active
                    task.save()
                else:
                    task.stock_active = True
                    task.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteAPIListAll(APIView):
    permission_classes = (IsAuthenticated, IsQAAndAdmin)

    def get(self, request):
        task = Task.objects.filter(
                time_point__isnull=False,
                point__isnull=False,
                stock_active=False,
                task_status="complete",).order_by('complete_time')

        serializer = TaskCompleteCheckOutSerializer(task, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#   03.01.2024
class StorageAPIList(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        storage = StorageStatus.objects.all()
        serializer = StorageSerializer(storage, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = StoragePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = request.data
            username = str(request.user.username)
            request_telegram_bot_team_lead(data, username)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def request_telegram_bot_team_lead(data, username):
    url = f"{TOKEN_TG_BOT}"

    updates = {'update_user': username}
    data = update_dict_values(data, updates)

    output_string = "\n".join([f"{key} - {value}" for key, value in data.items()])
    params = {
        'chat_id': ID_USER,
        'text': output_string,
    }
    requests.post(url, params=params)
    return True


def update_dict_values(original_dict, updates):
    """
    Обновляет значения в словаре original_dict с использованием значений из словаря updates.
    """
    for key, value in updates.items():
        if key in original_dict:
            original_dict[key] = value
    return original_dict


def aggregate_task_status_counts(task_type):
    return {
        'open': Task.objects.filter(task_type=task_type, task_status='open').count(),
        'in_progress': Task.objects.filter(task_type=task_type, task_status='in progress').count(),
        'waiting': Task.objects.filter(task_type=task_type, task_status='waiting').count(),
        'complete': Task.objects.filter(task_type=task_type, task_status='complete').count(),
        'checked': Task.objects.filter(task_type=task_type, task_status='checked').count(),
        'correcting': Task.objects.filter(task_type=task_type, task_status='correcting').count(),
    }


# def aggregate_project_status_counts(status_field):
#     # Создаем словарь с динамическим ключом и значением 'open', 'waiting' и т.д.
#     return {
#         'open': Project.objects.filter(**{status_field: 'open'}).count(),
#         'in_progress': Project.objects.filter(**{status_field: 'in progress'}).count(),
#         'checked': Project.objects.filter(**{status_field: 'checked'}).count(),
#     }


class DashboardStatusAPIList(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        a = Task.objects.filter(task_type="without", task_status='open').count()
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


class CheckedEmployeeAPIList(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        task = Task.objects.filter(task_status="checked", task_employee_user=user)
        serializer = TaskSerializer(task, many=True)
        return Response(serializer.data)


class CheckedTaskAllAPIList(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        task = Task.objects.filter(task_status="checked")
        serializer = TaskSerializer(task, many=True)
        return Response(serializer.data)


class TaskMessageAPIList(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, pk):
        task_message = TaskMessage.objects.filter(task_id=pk)
        serializer = TaskMessageSerializer(task_message, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        serializer = TaskMessageSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=user)

            image_data = request.FILES.getlist('message_image')

            # Create ProjectsImage instances and associate them with the Building instance
            for screenshot_data in image_data:
                project_image = MessageImage.objects.create(img=screenshot_data)
                instance.message_image.add(project_image)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TasksCreateListAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        tasks = Task.objects.filter(task_type_group="no projects").order_by('id')
        serializer = TasksListSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TasksCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskUpdateAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, pk):
        tasks = get_object_or_404(Task, id=pk)
        serializer = TasksCreateSerializer(tasks)
        return Response(serializer.data)

    def patch(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        serializer = TasksCreateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # new_employee_user = serializer.validated_data.get('task_employee_user')
            # if task.task_employee_user == new_employee_user or new_employee_user is None:
            #     serializer.save()
            #     print("a")
            # else:
            #     serializer.save(stock_active=True)
            #     print("B")
            return Response("Таск успешно обновлен", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectsFilterTegCreateAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        tasks = ProjectsFilterTeg.objects.all()
        serializer = ProjectsFilterTegSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        print(request.data)
        serializer = ProjectsFilterTegSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectsFilterTegUpdateAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None):
        # Получение одного объекта для обновления
        try:
            task = ProjectsFilterTeg.objects.get(pk=pk)
        except ProjectsFilterTeg.DoesNotExist:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectsFilterTegSerializer(task)
        return Response(serializer.data)

    def patch(self, request, pk=None):
        # Попытка обновить существующий объект
        try:
            task = ProjectsFilterTeg.objects.get(pk=pk)
        except ProjectsFilterTeg.DoesNotExist:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectsFilterTegSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class TasksDataCreateListAPI(APIView):
#     permission_classes = (IsAuthenticated, )
#
#     def get(self, request):
#         tasks = JSONCalculateData.objects.all()
#         serializer = TasksDataCreateSerializer(tasks, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = TasksDataCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class TaskDataUpdateAPI(APIView):
#     permission_classes = (IsAuthenticated, )
#
#     def get(self, request, pk):
#         task = get_object_or_404(Task, id=pk)
#         try:
#             calculations = JSONCalculateData.objects.get(task_id=task.id)
#             serializer = TasksDataCreateSerializer(calculations)
#             return Response(serializer.data)
#         except JSONCalculateData.DoesNotExist:
#             raise NotFound("No JSONCalculateData found for the given task_id")
#
#     def patch(self, request, pk):
#         task = get_object_or_404(Task, id=pk)
#         calculations = JSONCalculateData.objects.get(task_id=task.id)
#         serializer = TasksDataCreateSerializer(calculations, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response("Таск успешно обновлен", status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
