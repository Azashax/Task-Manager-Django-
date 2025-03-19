from rest_framework import permissions


class IsDepartmentRender(permissions.BasePermission):
    allowed_roles = {
        "RenderQA",
        "RenderUploader",
        "RenderEnhancer",
        "RenderGeometry",
        "RenderAssetDesigner",
        "Render3dDesigner"
    }

    def has_permission(self, request, view):
        return request.user.role in self.allowed_roles

class IsEnhancer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "RenderEnhancer"


class IsRenderQa(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "RenderQA"


class IsRenderUploader(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "RenderUploader"


class IsUploaderOrQa(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "RenderUploader"