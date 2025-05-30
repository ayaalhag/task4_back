from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('task.urls')),
    path('api/', include('accounts.urls')),     
    path('api/', include('project.urls')),
    path('api/', include('Comments.urls')),  

]
