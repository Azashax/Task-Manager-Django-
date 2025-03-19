from django.contrib import admin
from .models import Project, Region, Task, StorageStatus, ProjectsFilterTeg
from import_export.admin import ImportExportModelAdmin


@admin.register(Region)
class RegionAdmin(ImportExportModelAdmin):
    list_display = ('name',)
    search_fields = ('name', )
    list_display_links = ('name',)


@admin.register(ProjectsFilterTeg)
class ProjectsFilterTegAdmin(ImportExportModelAdmin):
    list_display = ('id', 'teg',)
    search_fields = ('teg', )
    list_display_links = ('teg',)


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    list_display = ('id', 'project_name', 'region', 'project_type', 'project_teamlead_user', 'built',
                    'project_teg', 'exterior_status', 'project_status')
    search_fields = ('project_name', )
    list_display_links = ('project_name',)


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    list_display = ('id', 'project_task_name', 'task_type', 'task_status', 'stock_active',
                    'task_employee_user', 'checked_time', 'total_correcting', 'description')
    search_fields = ('project_task_name', )
    list_display_links = ('project_task_name',)
    list_filter = ('task_status', 'task_type', 'stock_active')

#   03.01.2024
@admin.register(StorageStatus)
class RegionAdmin(ImportExportModelAdmin):
    list_display = ('update_user', 'create_data', 'storage_task', 'before_status', 'after_status')
    list_display_links = ('update_user',)
    search_fields = ('storage_task__project_task_name', )

