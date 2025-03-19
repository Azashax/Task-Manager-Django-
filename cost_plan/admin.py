from django.contrib import admin
from .models import (Role, UserProduct, Project, Product, Task,
                     ProductData, TaskData, Tariff, TaskGroupData,
                     TypeData)
from import_export.admin import ImportExportModelAdmin

@admin.register(Role)
class RoleAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)


@admin.register(UserProduct)
class UserProductAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    filter_horizontal = ('roles',)

@admin.register(Tariff)
class TariffAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title',)
    list_filter = ('id', 'title',)
    search_fields = ('id', 'title',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'money', 'time', 'updated_at', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'project', 'time', 'money', 'updated_at', 'created_at')
    list_filter = ('project', 'created_at', 'updated_at')
    search_fields = ('title', 'project__title')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'product', 'duration')
    list_filter = ('product', 'updated_at', 'created_at')
    search_fields = ('title', 'product__title')


@admin.register(TypeData)
class TypeDataAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title',)
    search_fields = ('title',)

@admin.register(ProductData)
class ProductDataAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title',)
    search_fields = ('title',)

@admin.register(TaskGroupData)
class ProductDataAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title',)
    search_fields = ('title',)

@admin.register(TaskData)
class TaskDataAdmin(ImportExportModelAdmin):
    list_display = ('id', 'title', 'money_per_hour')
    search_fields = ('title',)
