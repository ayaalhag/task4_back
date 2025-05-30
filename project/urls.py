from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ProjectViewSet, ProjectMembershipViewSet

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('members', ProjectMembershipViewSet, basename='project-membership')
urlpatterns = [
    path('', include(router.urls)),
]
