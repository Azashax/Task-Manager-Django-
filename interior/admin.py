from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    Project, Region, Task, ProjectsFilterTeg,
    TaskImages, TaskFiles, TaskMessage,
    UserTaskStock, TaskForReview, UnassignedTasks, MessageImage,
    HistoryTasksTransaction
)


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title', 'status', 'team_lead_user', 'region', 'built')
    search_fields = ('id', 'title')
    list_display_links = ('id', 'title')
    list_filter = ('status', 'region')


@admin.register(Region)
class RegionAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    list_display = ('id', 'type', 'status', 'employee_user', 'project', 'point',)
    search_fields = ('id', 'type', 'status')
    list_display_links = ('id', 'type')
    list_filter = ('status', 'project')


@admin.register(ProjectsFilterTeg)
class ProjectsFilterTegAdmin(ImportExportModelAdmin):
    list_display = ('id', 'teg')
    search_fields = ('teg',)
    list_filter = ('teg',)


@admin.register(TaskImages)
class TaskImagesAdmin(ImportExportModelAdmin):
    list_display = ('id', 'task', 'file')
    search_fields = ('task__id', 'file')
    list_filter = ('task',)


@admin.register(TaskFiles)
class TaskFilesAdmin(ImportExportModelAdmin):
    list_display = ('id', 'task', 'file')
    search_fields = ('task__id', 'file')
    list_filter = ('task',)


@admin.register(TaskMessage)
class TaskMessageAdmin(ImportExportModelAdmin):
    list_display = ('id', 'task', 'message', 'create_at', 'update_at')
    search_fields = ('task__id', 'message')
    list_filter = ('task', 'create_at')


@admin.register(MessageImage)
class MessageImageAdmin(ImportExportModelAdmin):
    list_display = ('id', 'img')
    search_fields = ('id', )
    list_filter = ('id', )


@admin.register(UserTaskStock)
class UserTaskStockAdmin(ImportExportModelAdmin):
    list_display = ('id', 'task', 'position')
    search_fields = ('task__id',)
    list_filter = ('task',)


@admin.register(TaskForReview)
class TaskForReviewAdmin(ImportExportModelAdmin):
    list_display = ('id', 'task')
    search_fields = ('task__id', )
    list_filter = ('task', )


@admin.register(UnassignedTasks)
class UnassignedTasksAdmin(ImportExportModelAdmin):
    list_display = ('id', 'task')
    search_fields = ('task__id', )
    list_filter = ('task', )


@admin.register(HistoryTasksTransaction)
class HistoryTasksTransactionAdmin(ImportExportModelAdmin):
    list_display = ('id', 'task', 'changed_by', 'field_name', 'old_value', 'new_value', 'changed_at')
    search_fields = ('id', )
    list_filter = ('id', )
