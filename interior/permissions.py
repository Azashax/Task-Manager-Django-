from rest_framework import permissions


class IsTeamlead(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "Teamlead"


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "Admin"


class ExceptEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role != "Employee"


class IsAdminAndTeamlead(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "Admin" or request.user.role == "Teamlead"


class IsAdminAndManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "Admin" or request.user.role == "Manager"


