from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Task
from .serializers import TaskSerializer
from .permissions import CanEditTask
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
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
        
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Task deleted successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='search-all-tasks',permission_classes=[AllowAny])
    def search_all_tasks(self, request):
        queryset = Task.objects.all()
        filtered_qs = self.filter_queryset(queryset)
        serializer = self.get_serializer(filtered_qs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        task = self.get_object()
        history = task.history.all().order_by('-history_date')

        data = []
        previous_record = None

        for record in history:
            if previous_record is None:
                # أول سجل (الأحدث) ما في مقارنة، بس نقدر نحط إنه "تم إنشاء المهمة" أو "السجل الأول"
                changes = ["Created"]
            else:
                changes = []
                # نقارن بين الحقلين في السجل الحالي والسابق
                if record.status != previous_record.status:
                    changes.append("Status changed")
                if record.title != previous_record.title:
                    changes.append("Title changed")
                if record.description != previous_record.description:
                    changes.append("Description changed")
                if record.assignee_id != previous_record.assignee_id:
                    changes.append("Assignee changed")
                if record.is_pinned != previous_record.is_pinned:
                    changes.append("Pinned status changed")

                if not changes:
                    changes.append("No changes")

            data.append({
                "history_date": record.history_date,
                "history_user": record.history_user.username if record.history_user else None,
                "history_type": record.history_type,
                "changes": changes,
            })

            previous_record = record

        return Response(data, status=status.HTTP_200_OK)
