from rest_framework import permissions


class IsTeamlead(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "Teamlead"

