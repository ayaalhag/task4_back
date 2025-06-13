from django.contrib import admin
from django.urls import path, include
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic import TemplateView  # ⬅️ نستخدمه للعرض المباشر

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('api/accounts/', include('accounts.urls')),     
    path('Comments/', include('Comments.urls')),  
    # path('api/notifications/', include('notifications.urls')),
    # path('admin/', admin.site.urls),
    # path('accounts/', include('django.contrib.auth.urls')),  # ✅ واجهات تسجيل الدخول/الخروج الجاهزة
   
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),     
    path('accounts/', include('accounts.urls')), 
    path('accounts/', include('django.contrib.auth.urls')),  
    path('projects/', include('project.urls')),  
    path('tasks/', include('task.urls')),

]

