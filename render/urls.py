from django.urls import path, include
from .views import *


urlpatterns = [
    path('projects/create/', ProjectCreateAPI.as_view()),
    path('projects/<int:pk>/update/', ProjectUpdateAPI.as_view()),
    path('projects/<int:pk>/delete/', ProjectsDeleteAPI.as_view()),
    path('projects/file/<int:pk>/delete/', ProjectFileBrochureDeleteAPI.as_view(), name='project-file-delete'),
    path('projects/update-priority-enhancer/', ProjectUpdatePriorityEnhancerAPI.as_view()),
    path('projects/task/upload/', TaskFileUploadAPI.as_view()),
    path('projects/task/<int:pk>/update/', ProjectWithTasksUpdateAPI.as_view()),
    path('projects/<int:pk>/', ProjectDetailAPI.as_view()),
    path('projects', ProjectListFiltersAPI.as_view()),
    path('projects/task', ProjectListTasksFiltersAPI.as_view()),
    # path('projects/sort', RenderTaskBeginUpdateAPI.as_view()),
    path('task/download/<int:pk>/', DownloadTaskImage.as_view()),
    # path('task/download/image-after/<int:pk>/', DownloadTaskImageAfter.as_view()),
    path('projects/download/file/<int:pk>/', DownloadProjectsFile.as_view()),
    path('task/<int:pk>/', RenderTaskBeginUpdateAPI.as_view()),
    path('task/<int:pk>/full/', TaskUpdateAPI.as_view()),
    path('sub-task/<int:pk>/full/', SubTaskUpdateAPI.as_view()),
    path('task-images/task/<int:pk>', TaskImagesAPI.as_view()),
    path('task-images/<int:pk>', TaskImagesUpdateAPI.as_view()),
    path('task-images/message/<int:pk>/create', TaskImagesMessageCreateAPI.as_view()),
    path('task-images/message/<int:pk>', TaskImagesMessageDetailsAPI.as_view()),
    path('render-task/message/<int:pk>/create', RenderTaskMessageCreateAPI.as_view()),
    path('render-task/message/<int:pk>', RenderTaskMessageDetailsAPI.as_view()),
    path('render-task/<int:id>/delete/', RenderTaskDeleteAPI.as_view(), name='render-task-delete'),
    path('projects/performance/enhancer', PerformanceEnhancerAPI.as_view(), name='render-task-delete'),
    path('enhancer-task-active', EnhancerTaskActiveView.as_view(), name='enhancer-task-active'),
]

