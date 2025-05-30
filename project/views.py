from rest_framework import viewsets, permissions
from .models import Project, ProjectMembership
from .serializers import ProjectSerializer
from .permissions import IsProjectManager
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project, ProjectMembership
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .permissions import IsProjectManager

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        # Projects اللي المستخدم مشارك فيها حسب ProjectMembership
        projects = Project.objects.filter(projectmembership__user=user).distinct()
        return projects

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsProjectManager]
        elif self.action == 'create':
            # تسمح فقط للمستخدمين المصادق عليهم بإنشاء المشاريع
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    def destroy(self, request, *args, **kwargs):
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'detail': 'Project deleted successfully.'}, status=status.HTTP_200_OK)
        
User = get_user_model()

class ProjectMembershipViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_project(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return None

    @action(detail=True, methods=['post'], url_path='add-member')
    def add_member(self, request, pk=None):
        project = self.get_project(pk)
        if not project:
            return Response({'detail': 'Project not found.'}, status=404)

        if not IsProjectManager().has_object_permission(request, self, project):
            return Response({'detail': 'Not allowed.'}, status=403)

        user_id = request.data.get('user_id')
        role = request.data.get('role', 'member')

        if role not in ['manager', 'member']:
            return Response({'detail': 'Invalid role.'}, status=400)

        try:
            user = User.objects.get(id=user_id)
            membership, created = ProjectMembership.objects.get_or_create(
                user=user, project=project,
                defaults={'role': role}
            )
            if not created:
                return Response({'detail': 'User already a member.'}, status=400)

            return Response({'detail': 'Member added.'})
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=404)

    @action(detail=True, methods=['delete'], url_path='remove-member')
    def remove_member(self, request, pk=None):
        project = self.get_project(pk)
        if not project:
            return Response({'detail': 'Project not found.'}, status=404)

        if not IsProjectManager().has_object_permission(request, self, project):
            return Response({'detail': 'Not allowed.'}, status=403)

        user_id = request.data.get('user_id')
        try:
            membership = ProjectMembership.objects.get(user__id=user_id, project=project)
            membership.delete()
            return Response({'detail': 'Member removed.'})
        except ProjectMembership.DoesNotExist:
            return Response({'detail': 'Membership not found.'}, status=404)
        
