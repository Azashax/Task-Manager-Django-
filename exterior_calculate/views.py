from .calculate import calculate_project_time
from .serializers import *
from .models import ProjectExterior, Building, BuildingObjects, Floors, Details
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .permissions import IsExTeamLead, IsExTeamLeadManager
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.core.exceptions import SuspiciousFileOperation
from django.db.models import Prefetch
from .utils_views import process_patch_request
import time
# from User.serializers import UserSerializer, UserTeamSerializer
# from User.models import TeamsExterior, MyUser
# from rest_framework.exceptions import NotFound
# from datetime import timedelta
# from django.utils import timezone
# from rest_framework import serializers
# import json

'''  ------------------------------------------- Калькулятор -----------------------------------------  '''


''' Projects '''


class ProjectListCreateAPI(APIView):
    permission_classes = (IsAuthenticated, IsExTeamLeadManager)

    def get(self, request):
        user = request.user
        if user.role == "ExTeamlead":
            projects_exterior = ProjectExterior.objects.filter(project_ex_teamlead_user=user).order_by('-id')
        else:
            projects_exterior = ProjectExterior.objects.all().order_by('-id')
        serializer = ProjectListSerializer(projects_exterior, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectUpdateAPI(APIView):
    permission_classes = (IsAuthenticated, IsExTeamLeadManager)

    def get(self, request, project_id):
        project_exterior = get_object_or_404(ProjectExterior, pk=project_id)
        serializer = ProjectUpdateSerializer(project_exterior)
        return Response(serializer.data)

    def patch(self, request, project_id):
        project_exterior = get_object_or_404(ProjectExterior, pk=project_id)

        serializer = ProjectUpdateSerializer(project_exterior, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectsCalculateView(APIView):
    permission_classes = (IsAuthenticated, IsExTeamLeadManager)

    def post(self, request, project_id):
        try:
            project = get_object_or_404(
                ProjectExterior.objects.prefetch_related(
                    Prefetch(
                        "buildings",
                        queryset=Building.objects.prefetch_related(
                            Prefetch(
                                "building_objects",
                                queryset=BuildingObjects.objects.prefetch_related(
                                    Prefetch("floors", queryset=Floors.objects.prefetch_related("details"))
                                )
                            )
                        )
                    )
                ),
                pk=project_id
            )

            total_low, total_midl, total_high = calculate_project_time(project)
            project.finished_time_low = total_low
            project.finished_time_midl = total_midl
            project.finished_time_high = total_high
            project.save()

            return Response(
                {
                    "message": "Project calculation completed successfully.",
                    "finished_time_low": total_low,
                    "finished_time_midl": total_midl,
                    "finished_time_high": total_high,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Calculation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DownloadProjectExteriorAPI(APIView):
    def get(self, request, project_id):
        project_exterior = get_object_or_404(ProjectExterior, id=project_id)

        # Получение абсолютного пути к файлу на сервере
        file_path = project_exterior.texture.name

        try:
            # Получение объекта файла из хранилища S3
            file = default_storage.open(file_path)
        except SuspiciousFileOperation:
            return JsonResponse({'error': 'File not found'}, status=404)

        # Отправка файла как HTTP-ответ
        return FileResponse(file)


'''      --       Building       --     '''


class BuildingListCreateAPI(APIView):
    permission_classes = (IsAuthenticated, IsExTeamLeadManager)

    def get(self, request, project_id):
        buildings = Building.objects.filter(project_exterior=project_id)
        serializer = BuildingListCreateSerializer(buildings, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        # Копируем данные из request.data и добавляем project_id
        data = request.data.copy()
        data['project_exterior'] = project_id

        print("Received Data:", data)

        # Сериализация данных
        serializer = BuildingListCreateSerializer(data=data)
        if serializer.is_valid():
            # Сохранение Building объекта
            building_instance = serializer.save()

            # Обработка загруженных скриншотов
            screenshots_data = request.FILES.getlist('new_screenshots')
            print("Uploaded Screenshots:", screenshots_data)

            for screenshot_data in screenshots_data:
                project_image = ProjectsImage.objects.create(img=screenshot_data)
                building_instance.screenshots.add(project_image)
                time.sleep(2)
            # Успешный ответ
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Ошибки валидации
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BuildingUpdateDeleteDetailsAPI(APIView):
    permission_classes = (IsAuthenticated, IsExTeamLeadManager)

    def get(self, request, building_id):
        try:
            building = Building.objects.get(id=building_id)
        except Building.DoesNotExist:
            return Response({"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BuildingListCreateSerializer(building)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, building_id):
        try:
            building = Building.objects.get(id=building_id)
        except Building.DoesNotExist:
            return Response({"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND)

        screenshots_to_add = request.FILES.getlist('new_screenshots', None)  # Новые изображения
        screenshots_to_delete = request.data.getlist('remove_screenshots', [])
        # Создаём копию данных без ключей, относящихся к изображениям
        data = request.data.copy()
        data.pop("new_screenshots", None)
        data.pop("remove_screenshots", None)
        serializer = BuildingListCreateSerializer(building, data=data, partial=True)
        if serializer.is_valid():
            building = serializer.save()

            # Добавляем новые изображения
            for image in screenshots_to_add:
                building_image = ProjectsImage.objects.create(img=image)
                building.screenshots.add(building_image)
                time.sleep(2)
            # Удаляем указанные изображения
            ProjectsImage.objects.filter(id__in=screenshots_to_delete).delete()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, building_id):
        try:
            building = Building.objects.get(id=building_id)
            building.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BuildingObjects.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


'''      --        Objects       --      '''


class ObjectsListCreateAPI(APIView):
    permission_classes = (IsAuthenticated, IsExTeamLeadManager)

    def get(self, request, building_id):
        projects_exterior = BuildingObjects.objects.filter(building_id__id=building_id).order_by('-id')
        serializer = ObjectsListCreateSerializer(projects_exterior, many=True)
        return Response(serializer.data)

    def post(self, request, building_id):
        data = request.data.copy()
        data['building'] = building_id
        serializer = ObjectsListCreateSerializer(data=data)
        if serializer.is_valid():
            building_instance = serializer.save()
            # Get screenshots data from request
            screenshots_data = request.FILES.getlist('new_screenshots')

            # Create ProjectsImage instances and associate them with the Building instance
            for img in screenshots_data:
                project_image = ProjectsImage.objects.create(img=img)
                building_instance.screenshots.add(project_image)
                time.sleep(2)
            return Response({'object_id': serializer.data["id"]}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObjectsUpdateDeleteDetailsAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, object_id):
        building_objects = BuildingObjects.objects.get(id=object_id)
        serializer = ObjectsListCreateSerializer(building_objects)
        return Response(serializer.data)

    def patch(self, request, object_id):
        try:
            building_objects = BuildingObjects.objects.get(id=object_id)
        except BuildingObjects.DoesNotExist:
            return Response({"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND)

        return process_patch_request(building_objects, ObjectsListCreateSerializer, request)

    def delete(self, request, building_id, object_id):
        try:
            # Попытка получить объект по переданному идентификатору и удалить его
            project = BuildingObjects.objects.get(id=object_id)
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)  # Успешное удаление
        except BuildingObjects.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)  # Объект не найден
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # Прочие ошибки


'''     --      Floors       --       '''


class FloorsListCreateAPI(APIView):
    permission_classes = (IsAuthenticated, IsExTeamLeadManager)

    def get(self, request, object_id):
        projects_exterior = Floors.objects.filter(building_object__id=object_id).order_by('-id')
        serializer = FloorsListCreateSerializer(projects_exterior, many=True)
        return Response(serializer.data)

    def post(self, request, object_id):
        print(request.data)
        data = request.data.copy()
        data['building_object'] = object_id
        data.pop("new_screenshots", None)
        serializer = FloorsListCreateSerializer(data=data)
        if serializer.is_valid():
            floor_instance = serializer.save()
            print(serializer.data)
            # Get screenshots data from request
            screenshots_data = request.FILES.getlist('new_screenshots')

            # Create ProjectsImage instances and associate them with the Building instance
            for screenshot_data in screenshots_data:
                floor_image = ProjectsImage.objects.create(img=screenshot_data)
                floor_instance.screenshots.add(floor_image)
                time.sleep(2)
            return Response({'floors_id': serializer.data["id"]}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FloorsUpdateDeleteDetailsAPI(APIView):
    permission_classes = (IsAuthenticated, IsExTeamLeadManager)

    def get(self, request, floor_id):
        objects_detail = get_object_or_404(Floors, pk=floor_id)
        serializer = FloorsListCreateSerializer(objects_detail)
        return Response(serializer.data)

    def patch(self, request, floor_id):
        try:
            floor_objects = Floors.objects.get(id=floor_id)
        except Floors.DoesNotExist:
            return Response({"error": "Floor not found"}, status=status.HTTP_404_NOT_FOUND)

        return process_patch_request(floor_objects, FloorsListCreateSerializer, request)


'''      --       Details       --      '''


class DetailsListCreateAPI(APIView):
    permission_classes = (IsAuthenticated, IsExTeamLeadManager)

    def get(self, request, floor_id):
        projects_exterior = Details.objects.filter(floors__id=floor_id).order_by('-id')
        serializer = DetailsListCreateSerializer(projects_exterior, many=True)
        return Response(serializer.data)

    def post(self, request, floor_id):
        data = request.data.copy()
        data['floors'] = floor_id
        serializer = DetailsListCreateSerializer(data=data)
        if serializer.is_valid():
            detail_instance = serializer.save()

            # Get screenshots data from request
            screenshots_data = request.FILES.getlist('new_screenshots')

            # Create ProjectsImage instances and associate them with the Building instance
            for screenshot_data in screenshots_data:
                detail_image = ProjectsImage.objects.create(img=screenshot_data)
                detail_instance.screenshots.add(detail_image)
                time.sleep(2)
            return Response({'detail_id': serializer.data["id"]}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetailsUpdateDeleteDetailsAPI(APIView):
    permission_classes = (IsAuthenticated, IsExTeamLeadManager)

    def get(self, request, detail_id):
        objects_detail = get_object_or_404(Details, pk=detail_id)
        serializer = DetailsListCreateSerializer(objects_detail)
        return Response(serializer.data)

    def patch(self, request, detail_id):
        try:
            detail_objects = Details.objects.get(id=detail_id)
        except Details.DoesNotExist:
            return Response({"error": "Detail not found"}, status=status.HTTP_404_NOT_FOUND)

        return process_patch_request(detail_objects, DetailsListCreateSerializer, request)


''' TopologyHard '''


class TopologyHardMixin:
    """Общий функционал для обработки объектов в TopologyHard."""

    @staticmethod
    def get_building_instance(objects_id, type_obj):
        """Возвращает объект в зависимости от типа."""
        model_mapping = {
            "objects": BuildingObjects,
            "floors": Floors,
            "details": Details,
        }
        model = model_mapping.get(type_obj)
        if not model:
            raise ValueError("Invalid type_obj")

        try:
            return model.objects.get(id=objects_id)
        except model.DoesNotExist:
            raise ValueError(f"{type_obj.capitalize()} not found")


class TopologyHardListCreateView(APIView, TopologyHardMixin):

    def get(self, request, objects_id, type_obj):
        building_instance = self.get_building_instance(objects_id, type_obj)
        topology_hard_objects = building_instance.topology_hard.all()
        serializer = TopologyHardSerializer(topology_hard_objects, many=True)
        return Response(serializer.data)

    def post(self, request, objects_id, type_obj):
        # Получение данных из запроса
        title = request.data.get('title')
        description = request.data.get('description', '')
        data = request.data.get('data', {})
        new_screenshots = request.data.get('new_screenshots', [])

        # Проверка обязательных полей
        if not title:
            return Response({"error": "Title is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Создание нового объекта TopologyHard
            instance = TopologyHard.objects.create(
                title=title,
                description=description,
                data=data
            )

            # Добавляем новые скриншоты
            screenshots = [
                ProjectsImage.objects.create(image=image)
                for image in new_screenshots
            ]
            instance.screenshots.add(*screenshots)

            # Сохранение объекта
            instance.save()

            if objects_id and type_obj:
                building_instance = self.get_building_instance(objects_id, type_obj)
                building_instance.topology_hard.add(instance)

            # Сериализация и возврат данных
            serializer = TopologyHardSerializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Internal server error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TopologyHardUpdateDeleteView(APIView):
    def patch(self, request, topology_id):
        try:
            topology_instance = TopologyHard.objects.get(id=topology_id)
            # Вызов пользовательской функции обработки
            process_patch_request(topology_instance, TopologyHardSerializer, request)

            return Response({"message": "Данные успешно обновлены"}, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


















'''  ------------------------------------------- Task -----------------------------------------  '''
#
#
# class ActiveTeamLeadListCreateView(APIView):
#     permission_classes = (IsAuthenticated, IsExTeamLeadManager)
#
#     def get(self, request):
#         user = request.user
#         try:
#             team = TeamsExterior.objects.get(teamlead=user)
#         except TeamsExterior.DoesNotExist:
#             raise NotFound("У вас нет группы")
#         team_members = team.employees.values_list('id', flat=True)
#         users = MyUser.objects.filter(id__in=team_members).order_by('username')
#         user_serializer = UserSerializer(users, many=True)
#         data = user_serializer.data
#         for user_data in data:
#             tasks = ProjectExterior.objects.filter(
#                 project_ex_employee_user=user_data['id'],
#                 stock_active=True,
#             ).order_by('in_stock_active')
#             task_serializer = ProjectExteriorSerializer(tasks, many=True)
#             user_data['array'] = task_serializer.data
#         return Response(data, status=status.HTTP_200_OK)
#
#
# class StockEmployeeListView(APIView):
#     permission_classes = (IsAuthenticated, IsExTeamLeadManager)
#
#     def get(self, request):
#         user = request.user
#
#         projects = ProjectExterior.objects.filter(
#             stock_active=True,
#             project_ex_employee_user=user
#         ).select_related('ex_employee_projects').order_by('in_stock_active')
#
#         earliest_task = projects.first()
#
#         if earliest_task:
#             earliest_task.exterior_status = 'in progress'
#             earliest_task.save()
#
#         serializer = ProjectExteriorSerializer(projects, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class SecureTeamLeadListCreateView(APIView):
#     permission_classes = (IsAuthenticated, IsExTeamLeadManager)
#
#     def get(self, request):
#         user = request.user
#
#         #   листь усеров из группы тимлида
#         try:
#             team = TeamsExterior.objects.get(team_lead=user)
#         except TeamsExterior.DoesNotExist:
#             raise NotFound("У вас нет группы")
#         team_members = team.employees.values_list('id', flat=True)
#         team_members_objects = MyUser.objects.filter(id__in=team_members)
#         serializer_team = UserTeamSerializer(team_members_objects, many=True)
#         #   ------------------------------
#
#         project_ids = ProjectExterior.objects.filter(
#             project_ex_teamlead_user=user
#         ).values_list('id', flat=True)
#
#         tasks = ExteriorTask.objects.filter(
#             stock_active=False,
#             task_status__in=["open", "correcting", "waiting"],
#             project_exterior_id__in=[str(id) for id in project_ids]
#         )
#
#         serializer_task = ExteriorTaskSerializer(tasks, many=True)
#         data = {
#             "tasks": serializer_task.data,
#             "team_members": serializer_team.data
#         }
#         return Response(data, status=status.HTTP_200_OK)


# class SecureTeamLeadUpdateAPI(APIView):
#     permission_classes = (IsAuthenticated, IsExTeamLeadManager)
#
#     def get(self, request, pk):
#         task = get_object_or_404(ExteriorTask, id=pk)
#         serializer = ExteriorTaskSerializer(task)
#         return Response(serializer.data)
#
#     def patch(self, request, pk):
#         task = get_object_or_404(ExteriorTask, id=pk)
#         # Преобразование 'task_employee_user' в число, если это строка
#         task_employee_user = request.data.get('task_employee_user')
#         if task_employee_user is not None and not isinstance(task_employee_user, int):
#             try:
#                 task_employee_user = int(task_employee_user)
#             except ValueError:
#                 return Response({"task_employee_user": "Некорректное значение"}, status=status.HTTP_400_BAD_REQUEST)
#         request.data['task_employee_user'] = task_employee_user
#         serializer = ExteriorTaskSerializer(task, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             if task.task_status == "in progress":
#                 user_id = serializer.validated_data.get('task_employee_user')
#                 if user_id is not None:
#                     queryset = ExteriorTask.objects.filter(
#                         task_employee_user=user_id,
#                         stock_active=True
#                     ).only('in_stock_active').order_by('in_stock_active')
#                     if queryset.exists():
#                         task.stock_active = True
#                         task.save()
#
#             if task.task_status == "correcting":
#                 user_id = serializer.validated_data.get('task_employee_user')
#                 if user_id is not None:
#                     queryset = ExteriorTask.objects.filter(
#                         task_employee_user=user_id,
#                         stock_active=True
#                     ).only('in_stock_active').order_by('in_stock_active')
#                     if queryset.exists():
#                         a = queryset.first()
#                         b = queryset.filter(task_status="correcting").count()
#                         new_in_stock_active = a.in_stock_active + timedelta(milliseconds=b + 1)
#                         task.stock_active = True
#                         task.save()
#                         task.in_stock_active = new_in_stock_active
#                         task.save()
#                     else:
#                         task.stock_active = True
#                         task.save()
#             if task.task_status == "waiting":
#                 user_id = serializer.validated_data.get('task_employee_user')
#                 if user_id is not None:
#                     queryset = ExteriorTask.objects.filter(
#                         task_employee_user=user_id,
#                         stock_active=True
#                     ).only('in_stock_active').order_by('in_stock_active')
#                     if queryset.exists():
#                         a = queryset.first()
#                         b = queryset.filter(task_status="correcting").count() or 0
#                         new_in_stock_active = a.in_stock_active + ExteriorTaskSerializer(milliseconds=b + 1)
#                         task.stock_active = True
#                         task.save()
#                         task.in_stock_active = new_in_stock_active
#                         task.save()
#                     else:
#                         task.stock_active = True
#                         task.save()
#
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class SecureTeamLeadUpdateAPI(APIView):
#     permission_classes = (IsAuthenticated, IsExTeamLeadManager)
#
#     def get_task(self, pk):
#         return get_object_or_404(ExteriorTask, id=pk)
#
#     def validate_task_employee_user(self, task_employee_user):
#         if task_employee_user is not None and not isinstance(task_employee_user, int):
#             try:
#                 task_employee_user = int(task_employee_user)
#             except ValueError:
#                 raise serializers.ValidationError({"task_employee_user": "Некорректное значение"})
#         return task_employee_user
#
#     def update_stock_active(self, task, user_id):
#         queryset = ExteriorTask.objects.filter(
#             task_employee_user=user_id,
#             stock_active=True
#         ).only('in_stock_active').order_by('in_stock_active')
#
#         if queryset.exists():
#             a = queryset.first()
#             b = queryset.filter(task_status="correcting").count()
#             new_in_stock_active = a.in_stock_active + timezone.timedelta(milliseconds=b + 1)
#             task.stock_active = True
#             task.in_stock_active = new_in_stock_active
#             task.save()
#         else:
#             task.stock_active = True
#             task.save()
#
#     def patch(self, request, pk):
#
#         task = self.get_task(pk)
#
#         if task.task_status == "open":
#             serializer = ExteriorTaskUpdateSerializer(task, data=request.data, partial=True)
#         else:
#             serializer = ExteriorTaskSerializer(task, data=request.data, partial=True)
#
#         if serializer.is_valid():
#             serializer.save()
#
#             if task.task_employee_user is None:
#                 task_employee_user = self.validate_task_employee_user(request.data.get('task_employee_user'))
#                 task.task_employee_user = task_employee_user
#                 task.save()
#
#             if task.task_status in ["in progress", "correcting", "waiting"]:
#                 self.update_stock_active(task, task.task_employee_user)
#
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class ProjectsCheckedListCreateView(APIView):
#     pass
#
#
# class ProjectsCompleteListCreateView(APIView):
#     pass
#
#
# class ProjectExteriorListAllView(APIView):
#     pass
#



