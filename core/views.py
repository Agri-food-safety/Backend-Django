from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from .models import User, PlantType, DiseaseType, Report, Alert
from .serializers import (
    UserSerializer, PlantTypeSerializer, DiseaseTypeSerializer,
    ReportSerializer, AlertSerializer, UserRegistrationSerializer,
    UserLoginSerializer, UserProfileSerializer, UserProfileUpdateSerializer
)

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'data': {
                    'userId': str(user.id),
                    'phone': user.phone,
                    'fullName': user.full_name,
                    'role': user.role
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Registration failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        # For now, return a dummy response since we don't have authentication
        return Response({
            'success': True,
            'data': {
                'userId': '550e8400-e29b-41d4-a716-446655440000',
                'phone': request.data.get('phone', '213555123456'),
                'fullName': 'Ahmed Benali',
                'role': 'farmer'
            }
        })

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PlantTypeViewSet(viewsets.ModelViewSet):
    queryset = PlantType.objects.all()
    serializer_class = PlantTypeSerializer

class DiseaseTypeViewSet(viewsets.ModelViewSet):
    queryset = DiseaseType.objects.all()
    serializer_class = DiseaseTypeSerializer

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

class UserProfileView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserProfileSerializer(user)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                updated_user = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'data': {
                        'userId': str(updated_user.id),
                        'fullName': updated_user.full_name,
                        'city': updated_user.city,
                        'state': updated_user.state,
                        'gpsLat': updated_user.gps_lat,
                        'gpsLng': updated_user.gps_lng
                    }
                })
            return Response({
                'success': False,
                'message': 'Profile update failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND) 