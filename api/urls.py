from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, WorkoutSessionViewSet, WorkoutMetricViewSet
from . import auth_views  # Import the auth views

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='userprofile')
router.register(r'workouts', WorkoutSessionViewSet, basename='workout')
router.register(r'metrics', WorkoutMetricViewSet, basename='metric')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', auth_views.register, name='auth-register'),
    path('auth/login/', auth_views.login, name='auth-login'),
    path('auth/logout/', auth_views.logout, name='auth-logout'),
    path('auth/me/', auth_views.user_info, name='auth-user-info'),
    
    # API endpoints
    path('', include(router.urls)),
]