from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PlantHealthReportViewSet, AlertViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'reports', PlantHealthReportViewSet, basename='report')
router.register(r'alerts', AlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
]
