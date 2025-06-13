from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet
from .views import TasksByProjectView ,TaskCreateView, TaskUpdateView, TaskDeleteView ,AllTasksView

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('by-project/<int:project_id>/', TasksByProjectView.as_view(), name='tasks-by-project'),
    path('add/', TaskCreateView.as_view(), name='task-add'),
    path('<int:pk>/edit/', TaskUpdateView.as_view(), name='task-edit'),
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
    path('all/', AllTasksView.as_view(), name='all-tasks'),

]
