from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task, TaskLog
from .serializers import TaskSerializer, TaskLogSerializer
from .permissions import CanEditTask
from django.views import View
from .forms import TaskForm
from project.models import Project

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'due_date', 'project', 'assignee']
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(project__projectmembership__user=user) | Q(assignee=user)
        ).distinct()
        
    def get_permissions(self):
        if self.action == 'search_all_tasks':
           permission_classes = [AllowAny]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, CanEditTask]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        project = serializer.validated_data.get('project')
        user = self.request.user

        if project.manager != user and serializer.validated_data.get('assignee') != user:
            raise PermissionDenied("Only project manager or assignee can create tasks for this project.")
        
        serializer.save()

    def perform_update(self, serializer):
        task = self.get_object()
        user = self.request.user

        if task.project.manager != user and task.assignee != user:
            raise PermissionDenied("Only project manager or assignee can update this task.")

        # تخزين القيم القديمة
        old_data = {
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'assignee': task.assignee,
            'is_pinned': task.is_pinned,
            'due_date': task.due_date
        }

        updated_task = serializer.save()

        # تسجيل التغييرات في TaskLog
        for field in old_data:
            old = old_data[field]
            new = getattr(updated_task, field)
            if old != new:
                TaskLog.objects.create(
                    task=updated_task,
                    field_changed=field,
                    old_value=str(old) if old else '',
                    new_value=str(new) if new else '',
                    modified_by=user
                )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Task deleted successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='search-all-tasks', permission_classes=[AllowAny])
    def search_all_tasks(self, request):
        queryset = Task.objects.all()
        filtered_qs = self.filter_queryset(queryset)
        serializer = self.get_serializer(filtered_qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='logs')
    def logs(self, request, pk=None):
        task = self.get_object()
        logs = TaskLog.objects.filter(task=task).order_by('-modified_at')
        serializer = TaskLogSerializer(logs, many=True)
        return Response(serializer.data)

class TaskCreateView(LoginRequiredMixin, View):
    def get(self, request):
        project_id = request.GET.get('project_id')
        project = get_object_or_404(Project, id=project_id)

        # تحقق من الصلاحية: المدير فقط
        if project.manager != request.user:
            raise PermissionDenied("❌ ليس لديك صلاحية لإضافة مهمة في هذا المشروع")

        form = TaskForm(initial={'project': project})
        return render(request, 'task/task_form.html', {'form': form, 'project': project})

    def post(self, request):
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            project = task.project

            if project.manager != request.user and task.assignee != request.user:
                raise PermissionDenied("❌ لا يمكن إضافة مهمة إلا إذا كنت مدير المشروع أو المكلف بها")

            task.save()
            return redirect('tasks-by-project', project_id=task.project.id)
        return render(request, 'task/task_form.html', {'form': form})

class TaskUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        project = task.project

        if project.manager != request.user and task.assignee != request.user:
            raise PermissionDenied("❌ لا تملك صلاحية التعديل")

        form = TaskForm(instance=task)
        return render(request, 'task/task_form.html', {'form': form, 'project': project})

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        project = task.project

        if project.manager != request.user and task.assignee != request.user:
            raise PermissionDenied("❌ لا تملك صلاحية التعديل")

        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks-by-project', project_id=project.id)

        return render(request, 'task/task_form.html', {'form': form, 'project': project})

class TaskDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        project = task.project

        if project.manager != request.user and task.assignee != request.user:
            raise PermissionDenied("❌ لا تملك صلاحية الحذف")

        return render(request, 'task/task_confirm_delete.html', {'task': task})

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        project_id = task.project.id

        if task.project.manager != request.user and task.assignee != request.user:
            raise PermissionDenied("❌ لا تملك صلاحية الحذف")

        task.delete()
        return redirect('tasks-by-project', project_id=project_id)

class AllTasksView(TemplateView):
    template_name = 'task/task_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = Task.objects.select_related('project', 'assignee').all()
        return context

class TasksByProjectView(TemplateView):
    template_name = 'task/task_list_by_project.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs['project_id']
        context['tasks'] = Task.objects.filter(project_id=project_id)
        return context