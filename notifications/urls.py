from django.urls import path
from .views import NotificationListView, MarkNotificationAsReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notifications'),
    path('<int:pk>/mark-as-read/', MarkNotificationAsReadView.as_view(), name='mark-as-read'),
]
