from rest_framework import viewsets, permissions
from .models import Comment
from .serializers import CommentSerializer
from .permissions import CanEditComment

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditComment]

    def get_queryset(self):
        user = self.request.user
        # تعليقات المهام التي للمستخدم (عضو بالمشروع أو المدير)
        return Comment.objects.filter(task__project__projectmembership__user=user).distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
