from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.routers import DefaultRouter
from .views import *


urlpatterns = [
    path('projects-list/create', ProjectAPIListCreate.as_view()),
    path('projects-list/', ProjectAPIListCreate.as_view()),  # вывод всех проектов
    path('region/', RegionAPIList.as_view()),

    path('project/<int:pk>/', ProjectAPIUpdate.as_view()),
    path('project/update/<int:pk>/', ProjectDetailAPIUpdate.as_view()),

    path('projects', ProjectAPIList.as_view()),    # Не начертанные проекты
    path('project/team-lead/list/', ProjectTeamLeadAPIList.as_view()),  # проекты самих тимлидов
    path('project/team-lead/list/stock/', ProjectTeamLeadStockAPIList.as_view()),   # проекты для Exterior

    path('task/create', TaskCreateAPI.as_view()),    # Task

    # path('projects-list/', ProjectAPIListCreate.as_view()),    # вывод всех проектов

    path('complete-load/', CompleteLoadAPIList.as_view()),
    path('complete/', CompleteAPIList.as_view()),
    path('complete/<int:pk>/', CompleteUpdateAPIList.as_view()),

    path('stock/employee/', StockEmployeeAPIList.as_view()),
    path('stock/employee/<int:pk>/', StockAPIUpdateEmployee.as_view()),

    path('secure/', SecureTeamleadAPIList.as_view()),
    path('secure/<int:pk>/', SecureTeamleadUpdateAPI.as_view()),

    path('dashboard', DashboardAPIList.as_view()),
    path('dashboard/status-count/', DashboardStatusAPIList.as_view()),
    path('in-progress-all/', InProgressAllAPIList.as_view()),

    path('projects-filter/', ProjectsFilterTegCreateAPI.as_view()),
    path('projects-filter/<int:pk>/', ProjectsFilterTegUpdateAPI.as_view()),

    path('in-progress/', InProgressTeamleadAPIList.as_view()),
    path('in-progress/update/<int:pk>/', InProgressTeamleadAPIUpdate.as_view()),

    path('projects-list/stock/', ProjectsStockAPIList.as_view()),

    path('complete-all/', CompleteAPIListAll.as_view()),
    path('complete-all/<int:pk>/', CompleteUpdateAPIListAll.as_view()),

    #   03.01.2024
    path('storage/create', StorageAPIList.as_view()),
    path('storage/', StorageAPIList.as_view()),

    path('checked/employee/', CheckedEmployeeAPIList.as_view()),
    path('checked/all/', CheckedTaskAllAPIList.as_view()),

    path('task/<int:pk>/message/', TaskMessageAPIList.as_view()),

    path('tasks/', TasksCreateListAPI.as_view()),
    path('tasks/<int:pk>/', TaskUpdateAPI.as_view()),
]
