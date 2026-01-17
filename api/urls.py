from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, WorkoutSessionViewSet, WorkoutMetricViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet, basename='userprofile')
router.register(r'workouts', WorkoutSessionViewSet, basename='workout')
router.register(r'metrics', WorkoutMetricViewSet, basename='metric')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]