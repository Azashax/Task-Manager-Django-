from rest_framework import permissions


class IsExTeamLead(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "ExTeamlead"


class IsExTeamLeadManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "ExTeamlead" or request.user.role == "ExManager"
