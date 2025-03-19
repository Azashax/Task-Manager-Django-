from rest_framework import permissions
from rest_framework.response import Response
from djoser.views import UserViewSet
from rest_framework import generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAdminUser
from .models import MyUser, Teams
from .serializers import UserSerializer, ProjectTeamleadSerializer, UserTeamSerializer, TeamsSerializer,\
    TeamsCreateSerializer, MyUserSerializer
from project.serializers import ProjectSerializer, TaskSerializer
from project.models import Task, Project
from project.permissions import IsAdmin
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, IsAuthenticated
from rest_framework import generics, viewsets, mixins, status
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, Value, CharField, Q, Max, F, Avg, Sum, Count, FloatField
from django.db.models.functions import Cast, Round
from django.db import models
from rest_framework.exceptions import NotFound


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['role'] = user.role

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = MyUser.objects.all()
        search_query = request.query_params.get('user-name', None)
        if search_query:
            users = users.filter(first_name__istartswith=search_query)

        users_p = users.annotate(
            sorting_role=Case(
                When(role='Admin', then=Value('A')),
                When(role='Teamlead', then=Value('B')),
                When(role='Manager', then=Value('C')),
                When(role='QA', then=Value('D')),
                When(role='Employee', then=Value('E')),
                default=Value('O'),
                output_field=CharField(),
            ),
        ).order_by('sorting_role')
        serializer = UserSerializer(users_p, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user_id = pk

        # Определите поля заданий, которые вы хотите отслеживать (task_with, task_without и так далее)
        task_fields = ['task_with', 'task_without', 'task_assemble', 'task_gltf', 'task_upload']

        # Используйте Q-объект для создания условий для фильтрации проектов
        conditions = Q()
        for task_field in task_fields:
            conditions |= Q(**{f"{task_field}__task_employee_user_id": user_id, f"{task_field}__task_status": "checked"})

        projects_with_checked_tasks = Project.objects.filter(conditions)

        data = []

        for project in projects_with_checked_tasks:
            project_data = {
                'id': project.id,
                'project_name': project.project_name,
                'region': project.region.name if project.region else "None Region",
            }

            # for task_field in task_fields:
            #     if getattr(project, task_field) and getattr(project, task_field).task_status == 'checked':
            #         project_data[task_field] = 1
            #     else:
            #         project_data[task_field] = 0
            for task_field in task_fields:
                task = getattr(project, task_field)
                if task and task.task_status == 'checked' and task.task_employee_user_id == user_id:
                    project_data[task_field] = 1
                else:
                    project_data[task_field] = 0

            data.append(project_data)

        return Response(data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        current_date = datetime.now()
        current_month = current_date.month
        # user = get_object_or_404(MyUser, id=pk)
        user = MyUser.objects.get(id=pk)
        # Фильтруем задачи для данного пользователя с статусом "checked"
        serializer = UserSerializer(user)
        # Фильтруем задачи для данного пользователя с статусом "checked" и аннотируем средний балл
        avg_point_queryset = Task.objects.select_related('task_employee_user').\
            filter(task_employee_user=user, task_status='checked')

        # Получаем средний балл для всех задач
        count_task = avg_point_queryset.count() or 0
        avg_point = avg_point_queryset.aggregate(sum_point=Sum(F('point')))['sum_point'] or 0

        # Фильтруем задачи для текущего месяца и аннотируем средний балл за месяц
        avg_point_month = 0
        if count_task != 0:
            avg_point_month_queryset = avg_point_queryset.filter(checked_time__month=current_month)
            avg_point_month = avg_point_month_queryset.aggregate(sum_point=Sum(F('point')))['sum_point'] or 0

        data = serializer.data
        data['avg_point'] = round(avg_point, 2)
        data['month_point'] = round(avg_point_month, 2)
        data['count_task'] = count_task

        return Response(data, status=status.HTTP_200_OK)


class CustomUserCreateView(UserViewSet):
    permission_classes = (IsAuthenticated, IsAdmin)

    def get(self, request):
        projects = MyUser.objects.all()
        serializer = UserSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')  # Предполагается, что пароль передается в запросе
        user = MyUser.objects.create_user(username=username, password=password)
        # Добавьте остальные поля пользователя
        return Response({"detail": "Пользователь успешно создан."}, status=status.HTTP_201_CREATED)


class UserPermissionsView(generics.RetrieveUpdateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserProfileTeamLeadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        try:
            team = Teams.objects.get(teamlead=user)
        except Teams.DoesNotExist:
            raise NotFound("У вас нет группы")
        team_members = team.employees.values_list('id', flat=True)
        team_members1 = MyUser.objects.filter(id__in=team_members)
        user_serializer = UserTeamSerializer(team_members1, many=True)
        data = {
            "profile1": serializer.data,
            "teams1": user_serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class UserProfileEmployeeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_month = datetime.now().month
        user = request.user
        serializer = UserSerializer(user)

        # Фильтруем задачи для данного пользователя с статусом "checked" и аннотируем средний балл
        avg_point_queryset = Task.objects.select_related('task_employee_user').\
            filter(task_employee_user=user, task_status='checked')

        # Получаем средний балл для всех задач
        avg_point = avg_point_queryset.aggregate(sum_point=Sum(F('point')))['sum_point'] or 0

        # Фильтруем задачи для текущего месяца и аннотируем средний балл за месяц
        avg_point_month = 0
        avg_point_month_queryset = avg_point_queryset.filter(checked_time__month=current_month)
        count_task = avg_point_month_queryset.count() or 0
        if count_task != 0:
            avg_point_month = avg_point_month_queryset.aggregate(sum_point=Sum(F('point')))['sum_point'] or 0

        data = serializer.data
        data['avg_point'] = round(avg_point, 2)
        data['month_point'] = round(avg_point_month, 2)
        data['count_task'] = count_task
        return Response(data, status=status.HTTP_200_OK)


class UserTaskProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        task_fields = ['task_with', 'task_without', 'task_assemble', 'task_gltf', 'task_upload']
        # Используйте Q-объект для создания условий для фильтрации проектов
        conditions = Q()
        for task_field in task_fields:
            conditions |= Q(**{f"{task_field}__task_employee_user_id": user_id, f"{task_field}__task_status": "checked"})

        projects_with_checked_tasks = Project.objects.filter(conditions)

        data = []

        for project in projects_with_checked_tasks:
            project_data = {
                'id': project.id,
                'project_name': project.project_name,
                'region': project.region.name if project.region else "None Region",
            }

            for task_field in task_fields:
                if getattr(project, task_field) and getattr(project, task_field).task_status == 'checked':
                    project_data[task_field] = 1
                else:
                    project_data[task_field] = 0

            data.append(project_data)

        return Response(data, status=status.HTTP_200_OK)


class TeamsCreateView(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    def post(self, request, format=None):
        serializer = TeamsSerializer(data=request.data)
        if serializer.is_valid():
            teamlead = serializer.validated_data.get('teamlead')
            if teamlead and Teams.objects.filter(teamlead=teamlead).exists():
                return Response({"error": "Teamlead already has a team."}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamsAPIList(APIView):
    """Вывод списка проектов"""
    permission_classes = (IsAuthenticated, IsAdmin)    # IsAdminUser,

    def get(self, request, *args, **kwargs):
        teams = Teams.objects.all().order_by('id')
        serializer = TeamsSerializer(teams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TeamsCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamsAPIEmployeeUpdate(APIView):
    permission_classes = (IsAuthenticated, IsAdmin)

    def get(self, request, pk):
        task = get_object_or_404(Teams, id=pk)  # Используйте get_object_or_404
        serializer = TeamsSerializer(task)
        return Response(serializer.data)

    def patch(self, request, pk):
        new_employee_id = request.data.get("employees")  # получаем нового сотрудника из запроса
        teams = get_object_or_404(Teams, id=pk)

        # Получаем текущих сотрудников и добавляем/удаляем нового
        current_employees = set(teams.employees.values_list('id', flat=True))
        new_employee_id = int(new_employee_id)

        if new_employee_id not in current_employees:
            # Добавляем нового сотрудника
            current_employees.add(new_employee_id)
            serializer = TeamsCreateSerializer(teams, data={'employees': list(current_employees)}, partial=True)
        else:
            # Удаляем ушедшего сотрудника
            employee = get_object_or_404(MyUser, id=new_employee_id)
            teams.employees.remove(employee)
            serializer = TeamsCreateSerializer(teams, data={'employees': list(teams.employees.values_list('id', flat=True))}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListRoleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Получаем пользователей, которые не связаны ни с одной командой
        unassigned_users = MyUser.objects.filter(employee__isnull=True, teamlead__isnull=True)

        teamlead = unassigned_users.filter(role="Teamlead")
        employee = unassigned_users.filter(role="Employee")

        teamlead_serializer = UserSerializer(teamlead, many=True)
        employee_serializer = UserSerializer(employee, many=True)

        return Response({
            'teamlead': teamlead_serializer.data,
            'employee': employee_serializer.data,
        }, status=status.HTTP_200_OK)


class RatingListView(APIView):
    def get(self, request):
        current_month = datetime.now().month
        users = MyUser.objects.filter(role="Employee", is_active=True)

        # # Обновленный список полей для аннотации
        # users1 = users.annotate(
        #     tasks_completed=Count('task_employee_user',
        #                           filter=Q(task_employee_user__checked_time__month=current_month) & Q(
        #                               task_employee_user__task_status="checked")),
        #     total_points=Cast(
        #         Sum(
        #             Case(
        #                 When(
        #                     Q(task_employee_user__checked_time__month=current_month) &
        #                     Q(task_employee_user__task_status="checked"),
        #                     then=F('task_employee_user__point')
        #                 ),
        #                 default=Value(0),
        #                 output_field=FloatField()
        #             )
        #         ),
        #         FloatField()
        #     )
        # ).order_by('-total_points')

        users1 = users.annotate(
            tasks_completed=Count('task_employee_user',
                                  filter=Q(task_employee_user__checked_time__month=current_month) & Q(
                                      task_employee_user__task_status="checked")),
            total_points=Round(
                Cast(
                    Sum(
                        Case(
                            When(
                                Q(task_employee_user__checked_time__month=current_month) &
                                Q(task_employee_user__task_status="checked"),
                                then=F('task_employee_user__point')
                            ),
                            default=Value(0),
                            output_field=FloatField()
                        )
                    ),
                    FloatField()
                ),
                2  # Number of decimal places to round to
            )
        ).order_by('-total_points')

        serializer = MyUserSerializer(users1, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamUsersListView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        team_lead = request.user
        try:
            team = Teams.objects.select_related('teamlead').get(teamlead=team_lead)
        except Teams.DoesNotExist:
            raise NotFound("Team not found")
        users = team.employees.all()
        if not users.exists():
            raise NotFound("No users found for this team")
        serializer = UserTeamSerializer(users, many=True)
        return Response(serializer.data)
