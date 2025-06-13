from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Project, ProjectMembership
from .serializers import ProjectSerializer
from .permissions import IsProjectManager
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm  
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework.views import APIView

User = get_user_model()

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        data['manager'] = user.id  # تعيين المدير الحالي

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()

        # إضافة المدير كعضو مدير
        ProjectMembership.objects.create(user=user, project=project, role='manager')

        # إضافة باقي الأعضاء
        members_input = request.data.get("members_input", [])
        for member in members_input:
            try:
                user_obj = User.objects.get(id=member["user_id"])
                ProjectMembership.objects.get_or_create(
                    user=user_obj,
                    project=project,
                    defaults={"role": member.get("role", "member")}
                )
            except User.DoesNotExist:
                continue

        return Response(self.get_serializer(project).data, status=status.HTTP_201_CREATED)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(projectmembership__user=user).distinct()

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsProjectManager]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # معالجة الأعضاء
        members_input = request.data.get("members_input", [])

        # حذف الأعضاء السابقين (عدا المدير الحالي)
        ProjectMembership.objects.filter(project=instance).exclude(user=request.user).delete()

        for member in members_input:
            try:
                user_obj = User.objects.get(id=member["user_id"])
                ProjectMembership.objects.get_or_create(
                    user=user_obj,
                    project=instance,
                    defaults={"role": member.get("role", "member")}
                )
            except User.DoesNotExist:
                continue

        return Response(serializer.data)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Project deleted successfully.'}, status=status.HTTP_200_OK)

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

@method_decorator(login_required, name='dispatch')
class ProjectListHTMLView(TemplateView):
    template_name = 'project/project_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = Project.objects.filter(projectmembership__user=self.request.user).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        projects = Project.objects.filter(projectmembership__user=user).distinct()

        context['projects'] = []

        for project in projects:
            members = project.projectmembership_set.all()
            members_data = [
                {'username': m.user.username, 'role': m.role}
                for m in members
            ]
            
            context['projects'].append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'created_at': project.created_at,
                'manager': project.manager.username if project.manager else "غير محدد",
                'members': members_data
            })

        return context
 
class CreateProjectAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")
        description = request.data.get("description")
        members_input = request.data.get("members_input", [])

        if not name:
            return Response({"detail": "اسم المشروع مطلوب"}, status=status.HTTP_400_BAD_REQUEST)

        project = Project.objects.create(name=name, description=description)
        ProjectMembership.objects.create(user=request.user, project=project, role="manager")

        for member in members_input:
            user_id = member.get("user_id")
            role = member.get("role", "member")

            if not user_id or role not in ["manager", "member"]:
                continue

            try:
                user = User.objects.get(id=user_id)
                if user != request.user:  # لا تعيد إضافة المدير نفسه
                    ProjectMembership.objects.create(user=user, project=project, role=role)
            except User.DoesNotExist:
                continue

        return Response({"detail": "✅ تم إنشاء المشروع"}, status=status.HTTP_201_CREATED)
    
class ProjectCreateHTMLView(View):
    def get(self, request):
        form = ProjectForm()
        return render(request, 'project/project_create.html', {'form': form})

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = request.user
            project.save()
            ProjectMembership.objects.create(user=request.user, project=project, role='manager')
            messages.success(request, 'تم إنشاء المشروع بنجاح!')
            return redirect('projects-html')  # غيّر الاسم حسب URL المناسب
        return render(request, 'project/project_create.html', {'form': form})
    
