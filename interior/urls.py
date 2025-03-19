from django.urls import path
from .views import (
    DashboardAPIList, ProjectAPIListCreate,
    ProjectAPIDetailUpdate, RegionAPIListCreate,
    RegionAPIDetailUpdate, TaskAPIListCreate,
    TaskAPIDetailUpdate, ProjectsFilterTegAPIListCreate,
    ProjectsFilterTegAPIDetailUpdate, TaskImagesAPIListCreate,
    TaskImagesAPIDetailUpdate, TaskFilesAPIListCreate,
    TaskFilesAPIDetailUpdate, TaskMessageListCreateView, ProjectTasksAPIListCreate,
    EmployeeAPIList, TeamLeadAPIList,
    TasksForReviewAPIList, UnassignedTaskAPIList, TeamEmployeesTaskAPIList,
    UpdateTaskPositions, EmployeeTasksAPIList, RatingTasksAPIView, ProfileAPIDetails
)

urlpatterns = [

    path('dashboard', DashboardAPIList.as_view(), name='dashboard'),
    path('rating', RatingTasksAPIView.as_view(), name='rating'),
    # Projects
    path('projects', ProjectAPIListCreate.as_view(), name='projects-list-create'),
    path('projects/<int:pk>/', ProjectAPIDetailUpdate.as_view(), name='projects-retrieve-update-destroy'),
    path('projects/<int:pk>/tasks/', ProjectTasksAPIListCreate.as_view(), name='projects-list-task'),

    path('employee-list/', EmployeeAPIList.as_view(), name='employee-list'),
    path('team-lead-list/', TeamLeadAPIList.as_view(), name='team-lead-list'),

    # Task Stock
    path('unassigned-tasks/', UnassignedTaskAPIList.as_view(), name='unassigned-tasks'),
    path('team-employees-tasks/', TeamEmployeesTaskAPIList.as_view(), name='team-employees-tasks'),
    path('task-for-review/', TasksForReviewAPIList.as_view(), name='tasks-for-review'),
    path('employee-tasks/', EmployeeTasksAPIList.as_view(), name='employees-tasks'),

    # Regions
    path('regions', RegionAPIListCreate.as_view(), name='regions-list-create'),
    path('regions/<int:pk>/', RegionAPIDetailUpdate.as_view(), name='regions-retrieve-update-destroy'),

    # Tasks
    path('tasks', TaskAPIListCreate.as_view(), name='tasks-list-create'),
    path('tasks/<int:pk>/', TaskAPIDetailUpdate.as_view(), name='tasks-retrieve-update-destroy'),
    path('update-task-positions/', UpdateTaskPositions.as_view(), name='update-task-positions'),

    # Project Filter Teg
    path('projects-filter-teg', ProjectsFilterTegAPIListCreate.as_view(), name='projects-filter-teg-list-create'),
    path('projects-filter-teg/<int:pk>/', ProjectsFilterTegAPIDetailUpdate.as_view(), name='projects-filter-teg-retrieve-update-destroy'),

    # Task Images
    path('task-images', TaskImagesAPIListCreate.as_view(), name='task-images-list-create'),
    path('task-images/<int:pk>/', TaskImagesAPIDetailUpdate.as_view(), name='task-images-retrieve-update-destroy'),

    # Task Files
    path('task-files', TaskFilesAPIListCreate.as_view(), name='task-files-list-create'),
    path('task-files/<int:pk>/', TaskFilesAPIDetailUpdate.as_view(), name='task-files-retrieve-update-destroy'),

    # User Task Stock
    # path('user-task-stock', StockAPIList.as_view(), name='user-task-stock-list-create'),
    # path('user-task-stock/<int:pk>/', StockAPIDetailUpdate.as_view(), name='user-task-stock-retrieve-update-destroy'),

    # Task Messages
    path('task/<int:pk>/messages/', TaskMessageListCreateView.as_view(), name='task-messages'),

    # Profile
    path('profile/', ProfileAPIDetails.as_view(), name='profile'),
]
