from rest_framework.permissions import AllowAny
# from rest_framework import status
# from rest_framework.response import Response
from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserListSerializer
from django.contrib.auth import get_user_model
from django.views import View
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.contrib import messages  
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic import TemplateView

User = get_user_model()

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }

            return Response({
                'message': 'User created successfully',  
                'user': user_data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterHTMLView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "✅ تم تسجيل الحساب بنجاح!") 
            return redirect('home') 
        return render(request, 'registration/register.html', {'form': form})

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.AllowAny]

class UserListHTMLView(ListView):
    model = User
    context_object_name = 'users'
    template_name = 'users/user_list.html'

class LoginHTMLView(TemplateView):
    template_name = 'registration/login.html'