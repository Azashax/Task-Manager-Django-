from django.contrib import admin
from .models import Building, BuildingObjects, ProjectExterior, Details, Floors, TopologyHard, \
    ProjectsImage, ExteriorTask, AdditionalStructure
from import_export.admin import ImportExportModelAdmin

@admin.register(ProjectExterior)
class ProjectExteriorAdmin(ImportExportModelAdmin):
    list_display = ('id', 'project_name', 'project_ex_teamlead_user', 'project_ex_employee_user', 'exterior_status')
    search_fields = ('project_name', )
    list_display_links = ('project_name',)

@admin.register(ExteriorTask)
class ExteriorTaskAdmin(ImportExportModelAdmin):
    list_display = ('id', 'task_employee_user', 'project_exterior_id', 'stock_active', )
    search_fields = ('id', )
    list_display_links = ('id',)

@admin.register(BuildingObjects)
class BuildingObjectsAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('id', )
    list_display_links = ('id',)

@admin.register(TopologyHard)
class TopologyHardAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('id', )
    list_display_links = ('title',)

@admin.register(ProjectsImage)
class ProjectsImageAdmin(ImportExportModelAdmin):
    list_display = ('id', 'img')

@admin.register(Details)
class DetailsAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('id', )
    list_display_links = ('title',)


@admin.register(Building)
class BuildingAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title', 'mid_poly')
    search_fields = ('id', 'title')
    list_display_links = ('title',)


@admin.register(Floors)
class FloorsAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('id', )
    list_display_links = ('title',)


@admin.register(AdditionalStructure)
class AdditionalStructureAdmin(ImportExportModelAdmin):
    list_display = ('id',)
    search_fields = ('id', )
    list_display_links = ('id',)
