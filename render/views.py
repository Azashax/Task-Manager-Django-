from User.models import MyUser
from .models import ProjectListing, RenderTask, SubTask, ProjectFile, RenderTaskImages, MessageTaskImages, MessageRenderTask, RenderTaskStatusChange
from .serializers import ProjectListingSerializer, RenderTaskSerializer, SubTaskSerializer, \
     RenderTaskSubTaskSerializer, ProjectListingRenderTaskSubTaskSerializer, ProjectListingCountTaskSerializer, \
     ProjectFileSerializer, RenderTaskImagesSerializer, RenderTaskImagesFullSerializer, RenderTaskImagesMessageFullSerializer, \
     RenderTaskMessageFullSerializer, RenderTaskMessageUserSerializer, UserPerformanceSerializer, SimpleUserSerializer, EnhancerTaskActiveSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView, DestroyAPIView
from .paginations import PaginationProjects, ProjectTaskPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Case, When, IntegerField, Q, Value, F
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import date, datetime
from .permissions import IsDepartmentRender
from PIL import Image
import os
from django.utils import timezone
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


class ProjectCreateAPI(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def post(self, request, *args, **kwargs):
        serializer = ProjectListingSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            return Response({'project_id': project.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectUpdateAPI(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def patch(self, request, *args, **kwargs):
        # Получаем ID проекта из URL или данных запроса
        project_id = kwargs.get('pk') or request.data.get('id')
        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Получаем проект по ID
            project = ProjectListing.objects.get(id=project_id)
        except ProjectListing.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        # Обновляем данные проекта
        serializer = ProjectListingSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            project = serializer.save()
            return Response({'project_id': project.id}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class ProjectUpdatePriorityEnhancerAPI(APIView):
    # permission_classes = (IsAuthenticated, IsDepartmentRender)
    def patch(self, request):
        return Response({"message": "Priority updated for projects where applicable."}, status=status.HTTP_200_OK)


""" Код для записи информации фотографии ( всех фотографии ) """
# import requests
# from PIL import Image
# from io import BytesIO
# import time
#
# def get_image_info_from_url(image_url, timeout=2):
#     try:
#         # Выполняем HTTP-запрос для получения изображения
#         response = requests.get(image_url, timeout=timeout)
#
#         if response.status_code == 200:
#             file_data = response.content  # Получаем данные файла
#
#             # Используем PIL для работы с изображением
#             image = Image.open(BytesIO(file_data))
#             width, height = image.size
#
#             # Информация о файле
#             file_size_mb = len(file_data)
#             file_extension = image.format.lower()
#             modification_time = response.headers.get('Last-Modified', 'Unknown')
#
#             # Возвращаем информацию об изображении
#             return {
#                 "width": width,
#                 "height": height,
#                 "file_size_mb": file_size_mb,
#                 "file_extension": f".{file_extension}",
#                 "modification_time": modification_time,
#             }
#         else:
#             print(f"Error retrieving image: HTTP {response.status_code}")
#             return None
#     except Exception as e:
#         print(f"Error retrieving image info: {e}")
#         return None
#
# def request_telegram_bot_errors(taskId):
#     url = f"https://api.telegram.org/bot6464128339:AAHgkDm3EZHoGmXV1I3m72vBDg41LB5nnLg/sendMessage"
#
#     output_string = f"task Id ({taskId})"
#     params = {
#         'chat_id': '591456032',
#         'text': output_string,
#     }
#     requests.post(url, params=params)
#     return True
#
#
# class ProjectUpdatePriorityEnhancerAPI(APIView):
#     def patch(self, request):
#         date_threshold = datetime(2024, 8, 30)
#
#         # Фильтрация всех задач, созданных до 30 августа 2024 года
#         tasks = RenderTask.objects.filter(id__range=(6000, 6100)).order_by('id')
#         print(f"Найдено {tasks.count()} задач, созданных до {date_threshold}.")
#         # Замер времени для всей операции
#
#         updated_tasks = []
#         total_processing_time = 0  # Общее время обработки всех задач
#         total = 0
#         total_image = 0
#         for task in tasks:
#             task_start_time = time.time()
#             # Получаем абсолютные URL для изображений image_after и image_before
#             image_after_url = f"https://d1kpxe5geks6lx.cloudfront.net/{task.image_after.name}" if task.image_after else None
#             image_before_url = f"https://d1kpxe5geks6lx.cloudfront.net/{task.image_before.name}" if task.image_before else None
#             # Если оба изображения пусты, пропускаем задачу
#             if not image_after_url and not image_before_url:
#                 print(f"Пропускаем задачу {task.id}: оба изображения image_after и image_before пусты")
#                 continue
#
#             # Обработка image_after
#             if image_after_url:
#                 image_after_info = get_image_info_from_url(image_after_url)
#                 if image_after_info:
#                     print(f"Информация об image_after для задачи {task.id}: {image_after_info}")
#                     task.image_after_info = image_after_info
#                     total_image += 1
#                 else:
#                     print(f"Не удалось получить информацию об image_after для задачи {task.id}")
#                     request_telegram_bot_errors(task.id)
#
#             # Обработка image_before
#             if image_before_url:
#                 image_before_info = get_image_info_from_url(image_before_url)
#                 if image_before_info:
#                     print(f"Информация об image_before для задачи {task.id}: {image_before_info}")
#                     task.image_before_info = image_before_info
#                     total_image += 1
#                 else:
#                     print(f"Не удалось получить информацию об image_before для задачи {task.id}")
#                     request_telegram_bot_errors(task.id)
#
#             task_end_time = time.time()
#             print(task_end_time)
#             task_processing_time = task_end_time - task_start_time
#             print(task_processing_time)
#             total_processing_time += task_processing_time
#             print(total_processing_time)
#             # Сохраняем задачу, если обновлены данные для одного из полей
#             if task.image_after_info or task.image_before_info:
#                 task.save()
#                 updated_tasks.append(task.id)
#             print("task: _", total)
#             print("image: _", total_image)
#             total += 1
#         return Response({
#             "updated_tasks": updated_tasks,
#             "message": "Информация о изображениях успешно обновлена для обработанных задач."
#         }, status=status.HTTP_200_OK)

""" ------------------------------------------------------------------------------------------ """


class TaskFileUploadAPI(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        project_id = request.data.get('project_id')

        try:
            project = ProjectListing.objects.get(id=project_id)
        except ProjectListing.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        files = request.FILES.getlist('file')

        tasks = []
        for file in files:
            file_type = file.name.split('_')[0]  # Assuming type is part of the file name
            print(f"Processing file: {file.name}, determined type: {file_type}")

            if file_type == 'brochure':
                file_serializer = ProjectFileSerializer(data={'project_file_id': project.id, 'file': file})
                if file_serializer.is_valid():
                    file_instance = file_serializer.save()
                    tasks.append(file_serializer.data)
                    print(f"Saved file as brochure: {file.name}")
                else:
                    print(f"Errors in brochure file_serializer: {file_serializer.errors}")
                    return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                print("file", file)
                # Если это InMemoryUploadedFile, можно работать так:
                if isinstance(file, InMemoryUploadedFile):
                    image = Image.open(BytesIO(file.read()))
                    file.seek(0)  # Возвращаем указатель на начало файла после чтения

                # Получение информации
                file_size_mb = round(file.size / (1024 * 1024), 2)
                file_extension = os.path.splitext(file.name)[1]
                width, height = image.size
                modification_time = timezone.now().isoformat()
                image_before_info = {
                    "file_size_mb": file_size_mb,
                    "file_extension": file_extension,
                    "modification_time": modification_time,
                    "width": width,
                    "height": height,
                }
                task_serializer = RenderTaskSerializer(data={
                    'project_id': project.id,
                    'image_before': file,
                    'type': "floor_plan" if file_type == "floorplan" else file_type,
                    'image_before_info': image_before_info,
                })
                print("a")
                #  task_serializer = RenderTaskSerializer(data={'project_id': project.id, 'image_before': file, 'type': "floor_plan" if file_type == "floorplan" else file_type})

                if task_serializer.is_valid():
                    task = task_serializer.save()
                    print(task_serializer.data)
                    tasks.append(task_serializer.data)
                    project = task.project_id  # Project instance related to the task

                    if file_type == "render" and project.render_check:
                        project.render_check = False
                    elif file_type == "floorplan" and project.floor_plan_check:
                        project.floor_plan_check = False

                    if project.sorted:
                        project.sorted = False

                    if project.status == "checked":
                        project.status = "open"

                    project.save()
                    print(f"Saved file as task: {file.name}")
                else:
                    print(f"Errors in task_serializer: {task_serializer.errors}")
                    return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'tasks': tasks}, status=status.HTTP_201_CREATED)


class ProjectWithTasksUpdateAPI(UpdateAPIView):
    queryset = ProjectListing.objects.all()
    serializer_class = ProjectListingSerializer
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        project_name = request.data.get('title')
        instance.title = project_name

        files = request.FILES.getlist('file')
        if len(files) > 1:
            instance.sorted = False
        instance.save()
        for file in files:
            file_type = file.name.split('_')[0]
            if file_type == 'brochure':
                ProjectFile.objects.create(project_file_id=instance, file=file)
            elif file_type == 'render':
                RenderTask.objects.create(project_id=instance, type='render', image_before=file)
            elif file_type == 'floorplan':
                RenderTask.objects.create(project_id=instance, type='floor_plan', image_before=file)

        return Response(serializer.data, status=status.HTTP_200_OK)


# from django.db.models import Count, Case, When, IntegerField, Q

def get_filtered_tasks(instance):
    # Аннотирование задач количеством подзадач типа 'asset' или 'geometry', статус которых не 'checked'
    annotated_tasks = instance.project_task.annotate(
        unchecked_subtasks_count=Count(
            Case(
                When(
                    Q(sub_task__status='checked') &
                    Q(sub_task__type__in=['asset', 'geometry']),
                    then=1
                ),
                output_field=IntegerField()
            )
        )
    )

    # Фильтрация задач, у которых есть подзадачи типа 'asset' или 'geometry' со статусом, отличным от 'checked'
    filtered_tasks = annotated_tasks.filter(
        unchecked_subtasks_count__gt=0
    )
    print(filtered_tasks)

    return filtered_tasks


class ProjectDetailAPI(RetrieveAPIView):
    queryset = ProjectListing.objects.all()
    serializer_class = ProjectListingRenderTaskSubTaskSerializer
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        user_role = request.user.role
        user_id = request.user.id
        print(user_role)  # Для отладки
        base_fields = [
            'id', 'type', 'status', 'new_task', 'project_id', 'image_before', 'image_after', 'task_employee_id',
            'task_qa_id', 'create_at', 'update_at'
        ]
        render_tasks = instance.project_task.none()
        if user_role in ['RenderQA', 'RenderUploader']:
            render_tasks = instance.project_task.all()
        elif user_role == 'Render3dDesigner':
            tasks_designer = get_filtered_tasks(instance).values_list(*base_fields)
            tasks_render = instance.project_task.filter(type='render').values_list(*base_fields)
            render_tasks = instance.project_task.filter(
                id__in=list(tasks_designer.union(tasks_render).values_list('id', flat=True)))
        elif user_role in ['RenderGeometry', 'RenderAssetDesigner']:
            sub_task_type = 'geometry' if user_role == 'RenderGeometry' else 'asset'
            tasks_specific = instance.project_task.filter(new_task=False, sub_task__type=sub_task_type)
            tasks_render = instance.project_task.filter(type='render')
            render_tasks = tasks_specific.union(tasks_render) if tasks_specific.exists() else tasks_render
        elif user_role == 'RenderEnhancer':

            render_tasks = instance.project_task.filter(
                Q(new_task=False) &
                Q(sub_task__type='correcting_2d') &
                (Q(sub_task__sub_task_employee_id__isnull=True) | Q(sub_task__sub_task_employee_id=user_id))
            )
        render_tasks = render_tasks.order_by('id')
        # render_tasks = render_tasks.exclude(sub_task=None)
        # Сериализация проекта и отфильтрованных RenderTask
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['project_task'] = RenderTaskSubTaskSerializer(render_tasks, many=True).data

        return Response(data)


class ProjectListTasksFiltersAPI(ListAPIView):
    serializer_class = ProjectListingRenderTaskSubTaskSerializer
    permission_classes = (IsAuthenticated, IsDepartmentRender)
    pagination_class = ProjectTaskPagination

    def get_queryset(self):
        # Фильтруем проекты, у которых есть project_task
        queryset = ProjectListing.objects.filter(project_task__isnull=False).distinct().prefetch_related('project_task__sub_task')
        print("Queryset: ", queryset)
        return queryset

    def filter_tasks_by_role(self, project_tasks, user_role):
        if user_role == 'Render3dDesigner':
            return project_tasks.filter(new_task=False, sub_task__type='render', sub_task__status="correcting")
        elif user_role == 'RenderGeometry':
            return project_tasks.filter(new_task=False, sub_task__type='geometry', sub_task__status="correcting")
        elif user_role == 'RenderAssetDesigner':
            return project_tasks.filter(new_task=False, sub_task__type='asset', sub_task__status="correcting")
        elif user_role == 'RenderEnhancer':
            return project_tasks.filter(new_task=False, sub_task__type='correcting_2d', sub_task__status="correcting")
        return project_tasks.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        user_role = request.user.role
        print("User role: ", user_role)

        filtered_projects = []
        for project in queryset:
            project_tasks = project.project_task.all()
            print("Project tasks for project {}: {}".format(project.id, project_tasks))
            render_tasks = self.filter_tasks_by_role(project_tasks, user_role).order_by('id')
            print("Filtered tasks for user role {}: {}".format(user_role, render_tasks))

            if render_tasks.exists():
                project_data = self.get_serializer(project).data
                project_data['project_task'] = RenderTaskSubTaskSerializer(render_tasks, many=True).data
                filtered_projects.append(project_data)
        total_count = len(filtered_projects)
        # Пагинация
        paginator = ProjectTaskPagination()
        page = paginator.paginate_queryset(filtered_projects, request)
        next_link = paginator.get_next_link()
        previous_link = paginator.get_previous_link()

        if page is not None:
            return paginator.get_paginated_response(page, total_count, next_link, previous_link)

        print("Filtered projects (non-paginated): ", filtered_projects)
        return Response(filtered_projects)


class ProjectListFiltersAPI(ListAPIView):
    serializer_class = ProjectListingCountTaskSerializer
    permission_classes = (IsAuthenticated, IsDepartmentRender)
    pagination_class = PaginationProjects
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['sorted', 'status', 'render_check', 'floor_plan_check', 'action_required', 'priority', 'priority_enhancer']
    search_fields = ['title', 'id']

    def get_queryset(self):
        user = self.request.user
        user_role = user.role
        status_filter = self.request.query_params.get('task-status')

        # Фильтрация по статусу correcting и роли пользователя
        filter_condition = Q()
        filter_condition &= Q(is_delete=False)
        annotations = {}
        # Базовые аннотации для всех ролей
        if user_role == 'RenderUploader' or user_role == 'RenderQA':
            annotations = {
                'total_tasks': Count(Case(
                    When(Q(project_task__type="floor_plan"), then=1),
                    output_field=IntegerField()
                    )),
                'complete_tasks': Count(Case(
                    When(Q(project_task__status='complete') & Q(project_task__type="floor_plan"), then=1),
                    output_field=IntegerField()
                    )),
                'in_progress_tasks': Count(Case(
                    When(Q(project_task__status='in_progress') & Q(project_task__type="floor_plan"), then=1),
                    output_field=IntegerField()
                    )),
                'correcting_tasks': Count(Case(
                    When(Q(project_task__status='correcting') & Q(project_task__type="floor_plan"), then=1),
                    output_field=IntegerField()
                    )),
                'checked_tasks': Count(Case(
                    When(Q(project_task__status='checked') & Q(project_task__type="floor_plan"), then=1),
                    output_field=IntegerField()
                    )),
                'open_tasks': Count(Case(
                    When(Q(project_task__status='open') & Q(project_task__new_task=False) & Q(project_task__type="floor_plan"), then=1),
                    output_field=IntegerField()
                    )),
                'new_tasks': Count(Case(
                    When(Q(project_task__new_task=True) & Q(project_task__type="floor_plan"), then=1),
                    output_field=IntegerField()
                    )),
                'total_tasks_render': Count(Case(
                    When(Q(project_task__type="render"), then=1),
                    output_field=IntegerField()
                    )),
                'complete_tasks_render': Count(Case(
                    When((Q(project_task__status='complete') & Q(project_task__sub_task__status='complete')) & Q(project_task__type="render"), then=1),
                    output_field=IntegerField()
                    )),
                'in_progress_tasks_render': Count(Case(
                    When(Q(project_task__status='in_progress') & Q(project_task__type="render"), then=1),
                    output_field=IntegerField()
                    )),
                'correcting_tasks_render': Count(Case(
                    When((Q(project_task__status='correcting') | Q(project_task__sub_task__status='correcting')) & Q(project_task__type="render"), then=1),
                    output_field=IntegerField()
                    )),
                'checked_tasks_render': Count(Case(
                    When(Q(project_task__status='checked') & Q(project_task__type="render"), then=1),
                    output_field=IntegerField()
                    )),
                'open_tasks_render': Count(Case(
                    When(Q(project_task__status='open') & Q(project_task__new_task=False) & Q(project_task__type="render"), then=1),
                    output_field=IntegerField()
                    )),
                'new_tasks_render': Count(Case(
                    When(Q(project_task__new_task=True) & Q(project_task__type="render"), then=1),
                    output_field=IntegerField()
                    )),
                }

        # Дополнительные аннотации для конкретных ролей
        elif user_role == 'Render3dDesigner':
            filter_condition &= Q(project_task__sub_task__type='render')
        elif user_role == 'RenderEnhancer':
            filter_condition &= ~Q(action_required="Waiting")
            annotations = {
                'in_progress_tasks_render': Count(Case(
                    When(Q(project_task__status='in_progress') & Q(project_task__type="render") & Q(project_task__sub_task__type='correcting_2d') & Q(project_task__sub_task__sub_task_employee_id=user.id), then=1),
                    output_field=IntegerField()
                )),
                'complete_tasks_render': Count(Case(
                    When(Q(project_task__status='complete') & Q(project_task__type="render") & Q(project_task__sub_task__type='correcting_2d') & Q(project_task__sub_task__sub_task_employee_id=user.id), then=1),
                    output_field=IntegerField()
                )),
                'correcting_tasks_render': Count(Case(
                    When(Q(project_task__type="render") & Q(project_task__status='correcting') & Q(project_task__sub_task__type='correcting_2d') & Q(project_task__sub_task__sub_task_employee_id=user.id), then=1),
                    output_field=IntegerField()
                )),
                'checked_tasks_render': Count(Case(
                    When(Q(project_task__status='checked') & Q(project_task__type="render") & Q(project_task__sub_task__type='correcting_2d') & Q(project_task__sub_task__sub_task_employee_id=user.id), then=1),
                    output_field=IntegerField()
                )),
                'open_tasks_render': Count(Case(
                    When(Q(project_task__status='open') & Q(project_task__type="render") & Q(project_task__sub_task__type='correcting_2d'), then=1),
                    output_field=IntegerField()
                )),
            }

            filter_condition &= Q(project_task__sub_task__type='correcting_2d') & (Q(project_task__status='open', project_task__new_task=False) | Q(project_task__sub_task__sub_task_employee_id=user.id))

        if status_filter == 'correcting':
            filter_condition &= Q(project_task__type="render", project_task__sub_task__status='correcting',
                                  project_task__sub_task__type='correcting_2d',
                                  project_task__sub_task__sub_task_employee_id=user.id)

        elif status_filter == 'checked':
            filter_condition &= Q(project_task__type="render", project_task__sub_task__status='checked',
                                  project_task__sub_task__type='correcting_2d',
                                  project_task__sub_task__sub_task_employee_id=user.id)

        elif status_filter == 'open':
            filter_condition &= Q(project_task__type="render",
                                  project_task__sub_task__type='correcting_2d')

        queryset1 = ProjectListing.objects.filter(filter_condition).order_by('-create_at')

        queryset = queryset1.annotate(**annotations)
        # Добавляем сортировку по priority_enhancer для роли RenderEnhancer
        priority_order = Case(
                    When(priority_enhancer='High Priority', then=Value(1)),
                    When(priority_enhancer='Medium Priority', then=Value(2)),
                    When(priority_enhancer='Low Priority', then=Value(3)),
                    When(priority_enhancer='None', then=Value(4)),
                    output_field=IntegerField(),
                )

        sort_field = self.request.query_params.get('sort', 'create_at')
        if sort_field in ['priority', 'priority_enhancer', 'listing_amt', 'action_required']:
            queryset = queryset.order_by(F(sort_field).asc(nulls_last=True))
        if user.role == 'RenderEnhancer':
            queryset = queryset.order_by(priority_order, '-create_at')
        if self.request.query_params.get('render_check'):
            queryset = queryset.order_by('-time_render_check')
        else:
            queryset = queryset.order_by('-create_at')
        return queryset


class DownloadTaskImage(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def patch(self, request, pk):
        try:
            task = RenderTask.objects.get(id=pk)

            if request.user.role == "RenderEnhancer":
                sub_task = task.sub_task.filter(type="correcting_2d").first()
                if sub_task and sub_task.sub_task_employee_id is None:
                    sub_task.sub_task_employee_id = request.user
                    sub_task.status = "in_progress"
                    sub_task.save()
                    if task.status == "open":
                        task.status = "in_progress"
                    task.save()
                    update_task_and_project(task)
                    return Response(status=status.HTTP_200_OK)

            if request.user.role == "Render3dDesigner":
                sub_task = task.sub_task.filter(type="render").first()
                if task.type == "floor_plan" and sub_task.sub_task_employee_id is None:
                    if sub_task:
                        sub_task.sub_task_employee_id = request.user
                        if sub_task.status == "open":
                            sub_task.status = "in_progress"
                            sub_task.save()
                        if task.status == "open":
                            task.status = "in_progress"
                        task.save()
                        update_task_and_project(task)
                        return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_200_OK)

            if request.user.role == "RenderGeometry":
                sub_task = task.sub_task.filter(type="geometry").first()
                if task.type == "floor_plan" and sub_task.sub_task_employee_id is None:
                    if sub_task:
                        sub_task.sub_task_employee_id = request.user
                        if sub_task.status == "open":
                            sub_task.status = "in_progress"
                            sub_task.save()
                        if task.status == "open":
                            task.status = "in_progress"
                        task.save()
                        update_task_and_project(task)
                        return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_200_OK)

            if request.user.role == "RenderAssetDesigner":
                sub_task = task.sub_task.filter(type="asset").first()
                if task.type == "floor_plan" and sub_task.sub_task_employee_id is None:
                    if sub_task:
                        sub_task.sub_task_employee_id = request.user
                        if sub_task.status == "open":
                            sub_task.status = "in_progress"
                            sub_task.save()
                        if task.status == "open":
                            task.status = "in_progress"
                        task.save()
                        update_task_and_project(task)
                        return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_200_OK)

            if task.status == "correcting" and request.user.role == "RenderEnhancer":
                sub_task = task.sub_task.filter(type="correcting_2d").first()
                if sub_task and sub_task.sub_task_employee_id is not None:
                    # sub_task.sub_task_employee_id = request.user
                    task.status = "in_progress"
                    task.save()
                    sub_task.status = "in_progress"
                    sub_task.save()
                    update_task_and_project(task)
                    return Response(status=status.HTTP_200_OK)

            return Response(
                status=status.HTTP_400_BAD_REQUEST)  # Возвращаем ошибку, если не удалось изменить статус задачи

        except RenderTask.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class DownloadTaskImageAfter(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def get(self, request, pk):
        try:
            task = RenderTask.objects.get(id=pk)

            if task.image_after:
                file_content = task.image_after.read()
                content_type = 'application/octet-stream'

                response = HttpResponse(file_content, content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{task.image_after.name}"'
                return response
            else:
                raise NotFound("File not found")

        except RenderTask.DoesNotExist:
            raise NotFound("Task not found")


class DownloadProjectsFile(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def get(self, request, pk):
        try:
            project_file = ProjectFile.objects.get(id=pk)

            # Получаем файл, обрабатывая случай его отсутствия
            file = project_file.file
            file_content = project_file.file.read() if file else None

            if file_content:
                content_type = 'application/octet-stream'
                response = HttpResponse(file_content, content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{project_file.file.name}"'
                return response
            else:
                return HttpResponse("Файл не найден", status=404)
        except ProjectFile.DoesNotExist:
            return HttpResponse("Файл не найден", status=404)


class TaskUpdateAPI(RetrieveUpdateAPIView):
    queryset = RenderTask.objects.all()
    serializer_class = RenderTaskSerializer
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class SubTaskUpdateAPI(RetrieveUpdateAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


def update_task_and_project(task):
    project = task.project_id

    # Получить все задачи, связанные с проектом
    project_tasks = project.project_task.all()

    # Проверить, если хотя бы одна задача имеет new_task == True
    has_new_task = project_tasks.filter(new_task=True).exists()

    # Проверить, если хотя бы одна задача имеет статус "in_progress"
    has_status = project_tasks.filter(status="in_progress").exists()

    # Проверить, все ли задачи имеют статус "checked"
    checked_status = project_tasks.filter(status="checked").count() == project_tasks.count()

    # Проверить, все ли задачи типа "render" имеют статус "checked"
    render_tasks = project_tasks.filter(type="render")
    render_checked_status = (
            0 < render_tasks.count() == render_tasks.filter(status="checked").count())

    floor_plan_tasks = project_tasks.filter(type="floor_plan")
    floor_plan_checked_status = (
            0 < floor_plan_tasks.count() == floor_plan_tasks.filter(status="checked").count())
    print("projects setting", project_tasks.filter(status="checked", type="render").count())
    print("projects setting", project_tasks.filter(type="render").count())
    print("projects setting", render_checked_status)

    # Обновить атрибуты проекта на основе проверок
    if not has_new_task:
        project.sorted = True

    if has_status:
        project.status = "in_progress"

    if render_checked_status:
        project.render_check = True

    if checked_status:
        project.status = "checked"

    if floor_plan_checked_status:
        project.floor_plan_check = True

    project.save()


class TaskImagesAPI(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, pk, *args, **kwargs):
        file_serializer = RenderTaskImagesSerializer(data=request.data, context={'task_id': pk})
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskImagesUpdateAPI(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def patch(self, request, pk, *args, **kwargs):
        try:
            task_image = RenderTaskImages.objects.get(pk=pk)
        except RenderTaskImages.DoesNotExist:
            return Response({'error': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)

        file_serializer = RenderTaskImagesFullSerializer(task_image, data=request.data, partial=True)
        if file_serializer.is_valid():
            file_serializer.validated_data['checked_is'] = False
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskImagesMessageCreateAPI(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def post(self, request, pk, *args, **kwargs):
        print(request.user)
        serializer = RenderTaskImagesMessageFullSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            try:
                render_task_image = RenderTaskImages.objects.get(pk=pk)
                if request.user.role == "RenderQA":
                    render_task_image.checked_is = True
                    render_task_image.status = "correcting"

                render_task_image.save()
            except RenderTaskImages.DoesNotExist:
                return Response({'error': 'RenderTaskImages not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskImagesMessageDetailsAPI(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def get(self, request, pk, *args, **kwargs):
        try:
            # Получаем объект сообщения по идентификатору
            message = MessageTaskImages.objects.filter(task_images=pk)
        except MessageTaskImages.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

        # Сериализуем объект сообщения
        serializer = RenderTaskImagesMessageFullSerializer(message, many=True)

        # Возвращаем данные сериализованного объекта
        return Response(serializer.data, status=status.HTTP_200_OK)


class RenderTaskMessageCreateAPI(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def post(self, request, pk, *args, **kwargs):
        print(request.data)
        data = request.data.copy()
        data['render_task_user_message'] = request.user.id
        serializer = RenderTaskMessageFullSerializer(data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if request.user.role == "RenderQA":
                render_task_id = serializer.data.get("render_task")
                if render_task_id:
                    try:
                        task = RenderTask.objects.get(id=render_task_id)

                        sub_task = task.sub_task.get(type="correcting_2d")
                        if sub_task:
                            if sub_task.status == "complete":
                                sub_task.status = "correcting"
                                sub_task.save()
                            if task.status == "complete":
                                task.status = "correcting"
                                task.save()
                            if sub_task.status == "checked":
                                sub_task.status = "correcting"
                                sub_task.save()
                            if task.status == "checked":
                                task.status = "correcting"
                                task.save()
                                project = task.project_id
                                if project.render_check:
                                    project.render_check = False
                                    project.save()
                        print(
                            f"RenderTask with ID {render_task_id} and SubTask with ID {sub_task.id} updated to status 'correcting'.")
                    except RenderTask.DoesNotExist:
                        print(f"RenderTask with ID {render_task_id} not found.")
                    except SubTask.DoesNotExist:
                        print(f"SubTask with type 'correcting_2d' not found for RenderTask with ID {render_task_id}.")
                else:
                    print("No valid render_task ID provided.")

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RenderTaskMessageDetailsAPI(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def get(self, request, pk, *args, **kwargs):
        try:
            # Получаем объект сообщения по идентификатору
            message = MessageRenderTask.objects.filter(render_task=pk)
        except MessageRenderTask.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

        # Сериализуем объект сообщения
        serializer = RenderTaskMessageUserSerializer(message, many=True)

        # Возвращаем данные сериализованного объекта
        return Response(serializer.data, status=status.HTTP_200_OK)


class RenderTaskBeginUpdateAPI(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def patch(self, request, pk):
        task = get_object_or_404(RenderTask, id=pk)
        user = request.user
        data = request.data

        if 'render2D' not in data and 'image_after_qa' not in data and 'approve' not in data and 'image_after' not in data \
                and 'geometry' not in data and 'render' not in data and 'asset' not in data and 'qa_status' not in data\
                and 'qa_corr_status' not in data and 'correcting_render' not in data and 'enhancer_status' not in data:
            return Response({"error": "Необходимо указать хотя бы одно из полей 'render2D', 'render3D', "
                                      "'image_after' или 'approve'"},
                            status=status.HTTP_400_BAD_REQUEST)

        if 'image_after' in data:
            file = request.data["image_after"]
            try:
                print(file)
                image = Image.open(file)

                # Получаем информацию о файле
                file_size_mb = round(file.size / (1024 * 1024), 2)  # размер файла в мегабайтах
                file_extension = os.path.splitext(file.name)[1]  # расширение файла
                width, height = image.size  # ширина и высота изображения
                modification_time = timezone.now().isoformat()  # текущее время в ISO формате

                image_after_info = {
                    "file_size_mb": file_size_mb,
                    "file_extension": file_extension,
                    "modification_time": modification_time,
                    "width": width,
                    "height": height,
                }
            except Exception as e:
                # В случае ошибки, сохраняем информацию о ней
                image_after_info = {
                    "error": str(e),
                    "modification_time": timezone.now().isoformat(),
                }
            task.image_after = file
            task.image_after_info = image_after_info
            try:
                sub_task = task.sub_task.get(type="correcting_2d")
            except task.sub_task.model.DoesNotExist:
                try:
                    sub_task = task.sub_task.get(type="render")
                except task.sub_task.model.DoesNotExist:
                    # Обработка случая, когда и суб-задача с типом 'correcting_2d', и с типом 'render' отсутствуют
                    pass
                else:
                    # Обработка случая, когда найдена суб-задача с типом 'render'
                    sub_task.uploaded = True
                    sub_task.save()
            else:
                # Обработка случая, когда найдена суб-задача с типом 'correcting_2d'
                sub_task.uploaded = True
                sub_task.save()

        if 'image_after_qa' in data:
            task.image_after = request.data["image_after_qa"]
            print(request.data["image_after_qa"])
            task.new_task = False
            if not SubTask.objects.filter(task_id=task, type="asset").exists():
                SubTask.objects.create(task_id=task, type="asset")
            if not SubTask.objects.filter(task_id=task, type="geometry").exists():
                SubTask.objects.create(task_id=task, type="geometry")
            if not SubTask.objects.filter(task_id=task, type="render").exists():
                SubTask.objects.create(task_id=task, type="render")

        if 'enhancer_status' in data:
            print(data)
            task.status = data["enhancer_status"]
            try:
                sub_task = task.sub_task.get(type="correcting_2d")
            except task.sub_task.model.DoesNotExist:
                try:
                    sub_task = task.sub_task.get(type="render")
                except task.sub_task.model.DoesNotExist:
                    # Обработка случая, когда и суб-задача с типом 'correcting_2d', и с типом 'render' отсутствуют
                    pass
                else:
                    # Обработка случая, когда найдена суб-задача с типом 'render'
                    sub_task.status = data["enhancer_status"]
                    sub_task.uploaded = False
                    sub_task.save()
            else:
                # Обработка случая, когда найдена суб-задача с типом 'correcting_2d'
                sub_task.status = data["enhancer_status"]
                sub_task.uploaded = False
                sub_task.save()

        if 'qa_status' in data:
            print(data)
            task.status = data["qa_status"]
            try:
                sub_task = task.sub_task.get(type="correcting_2d")
            except task.sub_task.model.DoesNotExist:
                try:
                    sub_task = task.sub_task.get(type="render")
                except task.sub_task.model.DoesNotExist:
                    # Обработка случая, когда и суб-задача с типом 'correcting_2d', и с типом 'render' отсутствуют
                    pass
                else:
                    # Обработка случая, когда найдена суб-задача с типом 'render'
                    sub_task.status = data["qa_status"]
                    sub_task.save()
            else:
                # Обработка случая, когда найдена суб-задача с типом 'correcting_2d'
                sub_task.status = data["qa_status"]
                sub_task.save()

        if 'qa_corr_status' in data:
            print(data["qa_corr_status"])
            task.status = "correcting"
            sub_task_corr = task.sub_task.get(type="render")
            sub_task_corr.status = "checked"
            sub_task_corr.save()
            SubTask.objects.create(task_id=task, type="correcting_2d")
            sub_task = task.sub_task.get(type="correcting_2d")
            sub_task.status = data["qa_corr_status"]
            sub_task.save()

        if 'qa_corr_designer_status' in data:
            print(data["qa_corr_status"])
            task.status = "correcting"
            sub_task_corr = task.sub_task.get(type="render")
            sub_task_corr.status = "correcting"
            sub_task_corr.save()

        if 'approve' in data:
            task.status = "checked"
            task.new_task = False
            task.task_qa_id = user

        if 'geometry' in data:
            sub_task = task.sub_task.filter(type="geometry").first()
            sub_task.status = data["geometry"]
            sub_task.save()

        if 'asset' in data:
            sub_task = task.sub_task.filter(type="asset").first()
            sub_task.status = data["asset"]
            sub_task.save()

        if 'correcting_render' in data:
            sub_task = task.sub_task.get(type="correcting_2d")
            sub_task.status = "checked"
            task.status = "checked"
            sub_task.save()

        if 'render2D' in data:
            task.new_task = False
            print(user.id)
            task.task_qa_id = user
            if not SubTask.objects.filter(task_id=task, type="correcting_2d").exists():
                SubTask.objects.create(task_id=task, type="correcting_2d")

        task.save()
        update_task_and_project(task)
        return Response({"success": "Статусы успешно обновлены"}, status=status.HTTP_200_OK)


class SubTaskStatusUpdateAPI(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def patch(self, request, pk):
        try:
            task = get_object_or_404(RenderTask, id=pk)
            sub_task_id = request.data.get("id")
            if not sub_task_id:
                return Response({"error": "Необходимо предоставить идентификатор подзадачи"},
                                status=status.HTTP_400_BAD_REQUEST)

            sub_task = get_object_or_404(SubTask, id=sub_task_id)

            in_progress = request.data.get("in_progress", False)
            status_value = request.data.get("status")

            # проверка статуса последного SubTask и по нему изменить Task
            if status_value == "checked":
                if sub_task.type in ["render", "correcting_2d"]:
                    task.status = "checked"
                    update_task_and_project(task)
            # проверка статуса последного SubTask и по нему изменить Task
            elif in_progress:
                if sub_task.type == "render" and task.status == "open":
                    task.status = "in_progress"
                elif sub_task.type in ["asset", "geometry"] and task.status == "open":
                    task.status = "in_progress"

            task.save()

            serializer = SubTaskSerializer(sub_task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"success": "Статус подзадачи успешно обновлен"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except (RenderTask.DoesNotExist, SubTask.DoesNotExist):
            return Response({"error": "Задача или подзадача не найдена"}, status=status.HTTP_404_NOT_FOUND)


class ProjectsListFilterSortedAPI(ListAPIView):
    queryset = ProjectListing.objects.all()
    serializer_class = ProjectListingSerializer
    permission_classes = (IsAuthenticated, IsDepartmentRender)
    pagination_class = PaginationProjects
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_fields = ['sorted']
    search_fields = ['title', "id"]


class RenderTaskDeleteAPI(DestroyAPIView):
    queryset = RenderTask.objects.all()
    permission_classes = (IsAuthenticated, IsDepartmentRender)
    lookup_field = 'id'
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # Проверка на наличие связанных SubTask
            related_subtasks = SubTask.objects.filter(task_id=instance)
            if related_subtasks.exists():
                related_subtasks.delete()
            self.perform_destroy(instance)
            update_task_and_project(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except RenderTask.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ProjectFileBrochureDeleteAPI(DestroyAPIView):
    queryset = ProjectFile.objects.all()
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProjectFile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProjectsDeleteAPI(DestroyAPIView):
    queryset = ProjectListing.objects.all()
    permission_classes = (IsAuthenticated, IsDepartmentRender)
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        try:
            project = self.get_object()
            # Удаление связанных задач RenderTask и их подзадач SubTask
            render_tasks = RenderTask.objects.filter(project_id=project)
            for task in render_tasks:
                task.sub_task.all().delete()  # Удаляем связанные SubTask
            render_tasks.delete()  # Удаляем RenderTask
            project.delete()  # Удаляем сам проект
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProjectListing.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PerformanceEnhancerAPI(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def get(self, request):
        enhancer = request.query_params.get('enhancer')  # Может быть "all" или id
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if not start_date or not end_date:
            start_date = date.today()
            end_date = date.today()
        else:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        users = MyUser.objects.filter(role='RenderEnhancer')
        all_users_serializer = SimpleUserSerializer(
            users,
            many=True
        )

        # Фильтрация по enhancer, если это не "all"
        if enhancer and enhancer != "all":
            try:
                enhancer_id = int(enhancer)
                users = users.filter(id=enhancer_id)
            except ValueError:
                return Response({"error": "Invalid enhancer ID."}, status=400)

        serializer = UserPerformanceSerializer(
            users,
            many=True,
            context={'enhancer': enhancer, 'start_date': start_date, 'end_date': end_date}
        )


        data = {
            "data": serializer.data,
            "users": all_users_serializer.data
        }
        return Response(data)


class EnhancerTaskActiveView(APIView):
    permission_classes = (IsAuthenticated, IsDepartmentRender)

    def get(self, request, *args, **kwargs):
        # Получаем параметры start_date и end_date из запроса
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Если даты не переданы, использовать текущую дату
        today = timezone.now().date()
        if not start_date or not end_date:
            start_date = today
            end_date = today
            print(start_date)
        else:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Фильтрация по промежутку дат
        changes = RenderTaskStatusChange.objects.filter(
            changed_at__date__gte=start_date,
            changed_at__date__lte=end_date,
        )
        print(changes)
        # Отбор пользователей с ролью RenderEnhancer
        enhancer_users = MyUser.objects.filter(role='RenderEnhancer')
        print(enhancer_users)
        result = []

        # Для каждого пользователя считаем количество задач в разных статусах
        for enhancer in enhancer_users:
            in_progress_count = changes.filter(changed_by=enhancer, new_status='in_progress').count()
            complete_count = changes.filter(changed_by=enhancer, new_status='complete').count()

            result.append({
                "enhancer_name": enhancer.username,  # Получаем полное имя пользователя
                "in_progress_count": in_progress_count,
                "complete_count": complete_count,
            })
        print(result)
        # Возвращаем данные в виде списка
        return Response(result)
