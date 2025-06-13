from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ProjectViewSet, ProjectMembershipViewSet ,ProjectListHTMLView
from .views import ProjectListHTMLView, ProjectCreateHTMLView ,CreateProjectAPIView

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('members', ProjectMembershipViewSet, basename='project-membership')
urlpatterns = [
    path('', ProjectListHTMLView.as_view(), name='projects-html'),
    path('create/', ProjectCreateHTMLView.as_view(), name='project-create'),
    path('create-project/', CreateProjectAPIView.as_view(), name='create-project'),
    # path('delete/', ProjectViewSet.as_view()),
    path('api/', include(router.urls)),

    # path('<int:pk>/edit/', ProjectEditHTMLView.as_view(), name='project-edit'),
    # path('projects/create/', ProjectCreateHTMLView.as_view(), name='project-create-html'),
    

]


# urlpatterns = [
#     path('', include(router.urls)),  # يجب أن يسبق أي مسار آخر
#     path('html/', ProjectListHTMLView.as_view(), name='projects-html'),
#     path('create/', ProjectCreateHTMLView.as_view(), name='project-create'),
# ]
