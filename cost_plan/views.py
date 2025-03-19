from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Project, ProductData, TaskData, Task, Product, Tariff, UserProduct, Role
from .serializers import (FullProjectSerializer, ProductDataSerializer, TaskDataDataSerializer, ProjectSerializer,
                          TariffSerializer, FullProductSerializer)
from .service import products_update_type_fields, tasks_update_time_money, products_deleted
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.utils.timezone import now
from datetime import timedelta

class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = FullProjectSerializer


class ProjectsListView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class TariffListView(generics.ListAPIView):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer


class ProductsDataListView(generics.ListAPIView):
    queryset = ProductData.objects.all()
    serializer_class = ProductDataSerializer


class TaskDataListView(generics.ListAPIView):
    queryset = TaskData.objects.all()
    serializer_class = TaskDataDataSerializer


class GanttGenerations(APIView):
    def get(self, request, pk):
        # Получаем проект и связанные продукты
        project = get_object_or_404(Project, id=pk)
        products = Product.objects.filter(project=project).prefetch_related('tasks')

        # Получаем все задачи проекта
        active_task = Task.objects.filter(archive_is=False)
        tasks = active_task.filter(product__in=products).select_related('product')

        return Response(
            {},
            status=status.HTTP_200_OK
        )


class ProductsAllUpdateView(APIView):
    def patch(self, request, pk, *args, **kwargs):
        # Получаем данные или пустой список, если ключ отсутствует
        products_data = request.data.get("products", [])
        del_products = request.data.get("delProducts", [])
        # Проверяем, что переданы списки
        if not isinstance(products_data, list) and not isinstance(del_products, list):
            return Response(
                {"error": "Ожидается список продуктов"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Вызываем функции обновления
        status_products = products_update_type_fields(products_data)
        products_deleted(del_products)
        return Response(
            {"status": status_products},
            status=status.HTTP_200_OK if status_products=="success" else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
