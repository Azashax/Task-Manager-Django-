from django.contrib import admin
from .models import ProjectListing, RenderTask, SubTask, ProjectFile, RenderTaskImages, MessageTaskImages, \
    MessageRenderTask, RenderTaskStatusChange, StorageActiveUser
from import_export.admin import ImportExportModelAdmin


@admin.register(ProjectListing)
class ProjectExteriorAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title', 'sorted', 'status', 'time_listing_update', 'render_check', 'floor_plan_check', 'priority', 'is_delete')
    search_fields = ('id', 'title')
    list_display_links = ('id',)
    list_filter = ('is_delete',)


@admin.register(RenderTask)
class RenderTaskAdmin(ImportExportModelAdmin):
    list_display = ('id', 'project_id', 'type', 'new_task', 'status', 'create_at')
    search_fields = ('id', 'project_id__id')
    list_display_links = ('id',)


@admin.register(RenderTaskImages)
class RenderTaskAdmin(ImportExportModelAdmin):
    list_display = ('id', )
    search_fields = ('id',)
    list_display_links = ('id',)


@admin.register(MessageTaskImages)
class RenderTaskAdmin(ImportExportModelAdmin):
    list_display = ('id', 'task_images')
    search_fields = ('id', 'task_images')
    list_display_links = ('id',)


@admin.register(MessageRenderTask)
class RenderTaskAdmin(ImportExportModelAdmin):
    list_display = ('id', 'render_task')
    search_fields = ('id', 'render_task__id')
    list_display_links = ('id',)


@admin.register(SubTask)
class SubTaskAdmin(ImportExportModelAdmin):
    list_display = ('id', 'task_id', 'type', 'status', 'sub_task_employee_id')
    search_fields = ('id', 'task_id__id')
    list_display_links = ('id',)


@admin.register(ProjectFile)
class ProjectFileExteriorAdmin(ImportExportModelAdmin):
    list_display = ('id', 'project_file_id')
    search_fields = ('id', 'project_file_id__id')
    list_display_links = ('id',)


@admin.register(StorageActiveUser)
class StorageActiveUserAdmin(ImportExportModelAdmin):
    list_display = ('id', 'user', 'action', 'fields', 'create_at')
    search_fields = ('id', 'action', 'create_at', 'user__username', 'fields')
    list_display_links = ('id',)


@admin.register(RenderTaskStatusChange)
class RenderTaskStatusChangeAdmin(ImportExportModelAdmin):
    list_display = ('id', 'task', 'project_name', 'old_status', 'new_status', 'changed_by', 'changed_at')
    search_fields = ('project_name', 'task__id', 'changed_by__username')
    list_display_links = ('id',)
    list_filter = ('new_status', 'changed_at')