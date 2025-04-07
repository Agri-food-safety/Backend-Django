from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, PlantTypeViewSet, DiseaseTypeViewSet,
    ReportViewSet, AlertViewSet, UserRegistrationView,
    UserLoginView, UserProfileView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'plant-types', PlantTypeViewSet)
router.register(r'disease-types', DiseaseTypeViewSet)
router.register(r'reports', ReportViewSet)
router.register(r'alerts', AlertViewSet)

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/profile/<uuid:user_id>/', UserProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]
