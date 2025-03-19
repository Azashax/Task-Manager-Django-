from django.urls import path
from .views import (
    ProductsDataListView, ProjectRetrieveUpdateDestroyView,
    TaskDataListView, ProjectsListView, ProductsAllUpdateView, GanttGenerations,
    TariffListView
)

urlpatterns = [
    path('task-data/', TaskDataListView.as_view(), name='task-data-list'),
    path('products-data/', ProductsDataListView.as_view(), name='products-data-list'),
    path('project/<int:pk>/products/update/', ProductsAllUpdateView.as_view(), name='products-data-list'),
    path('projects/<int:pk>/', ProjectRetrieveUpdateDestroyView.as_view(), name='project-detail'),
    path('projects/', ProjectsListView.as_view(), name='project-list'),
    path('tariff/', TariffListView.as_view(), name='tariff-list'),
    path('projects/<int:pk>/gantt/', GanttGenerations.as_view(), name='project-gantt'),
]
