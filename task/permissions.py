from rest_framework.permissions import BasePermission

class CanEditTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.project.manager == user or obj.assignee == user
