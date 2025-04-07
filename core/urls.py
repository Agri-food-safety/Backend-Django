from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, PlantTypeViewSet, DiseaseTypeViewSet,
    ReportViewSet, AlertViewSet, UserRegistrationView,
    UserLoginView, UserProfileView, PlantDetectionView,
    DiseaseDetectionView, PestDetectionView, DroughtDetectionView,
    ReportStatusUpdateView, PestTypeViewSet
)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'plant-types', PlantTypeViewSet)
router.register(r'disease-types', DiseaseTypeViewSet)
router.register(r'pest-types', PestTypeViewSet)
router.register(r'reports', ReportViewSet)
router.register(r'alerts', AlertViewSet)

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('detect/plant/', PlantDetectionView.as_view(), name='plant-detection'),
    path('detect/disease/', DiseaseDetectionView.as_view(), name='disease-detection'),
    path('detect/pest/', PestDetectionView.as_view(), name='pest-detection'),
    path('detect/drought/', DroughtDetectionView.as_view(), name='drought-detection'),
    path('reports/<uuid:report_id>/status/', ReportStatusUpdateView.as_view(), name='report-status-update'),
    path('', include(router.urls)),
]
