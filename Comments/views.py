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
        comment = serializer.save(author=self.request.user)

        task = comment.task
        # followers = task.followers.all()  # سنضيف Model TaskFollower لاحقًا
        assignee = task.assignee

        notified_users = set()

        # # إخطار المكلف إن لم يكن هو صاحب التعليق
        # if assignee and assignee != comment.author:
        #     Notification.objects.create(
        #         target_user=assignee,
        #         message=f"تم إضافة تعليق على المهمة: {task.title}",
        #         task=task,
        #         comment=comment
        #     )
        #     notified_users.add(assignee)

        # # إخطار المتابعين الآخرين
        # for follower in followers:
        #     user = follower.user
        #     if user != comment.author and user not in notified_users:
        #         Notification.objects.create(
        #             target_user=user,
        #             message=f"تم إضافة تعليق جديد على المهمة: {task.title}",
        #             task=task,
        #             comment=comment
        #         )
