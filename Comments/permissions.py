from rest_framework.permissions import BasePermission

class CanEditComment(BasePermission):
    def has_object_permission(self, request, view, obj):
        # فقط صاحب التعليق أو مدير مشروع المهمة يقدر يعدل أو يحذف
        user = request.user
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.author == user or obj.task.project.manager == user
        # السماح لكل المستخدمين المسجلين بقراءة التعليقات
        return request.method in ['GET', 'HEAD', 'OPTIONS']
