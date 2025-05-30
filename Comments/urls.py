from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CommentViewSet

router = DefaultRouter()
router.register('comments', CommentViewSet, basename='comment')

app_name = 'comments'

urlpatterns = [
    path('', include(router.urls)),
]
