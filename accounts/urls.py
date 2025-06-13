from django.urls import path
from .views import RegisterAPIView, RegisterHTMLView, UserListView ,UserListHTMLView ,LoginHTMLView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/html/', RegisterHTMLView.as_view(), name='register'),  
    path('register/', RegisterAPIView.as_view(), name='register-api'), 
    path('login/html/', LoginHTMLView.as_view(), name='login-html'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/html/', UserListHTMLView.as_view(), name='user-list-html'),

]
