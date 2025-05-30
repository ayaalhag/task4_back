from rest_framework import permissions

class IsProjectManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        manager = obj.manager
        if not manager:
            return False
        return request.user == manager
