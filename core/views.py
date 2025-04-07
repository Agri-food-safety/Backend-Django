from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime
from .models import User, PlantType, DiseaseType, Report, Alert
from .serializers import (
    UserSerializer, PlantTypeSerializer, DiseaseTypeSerializer,
    ReportSerializer, AlertSerializer, UserRegistrationSerializer,
    UserLoginSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    PlantDetectionRequestSerializer, PlantDetectionResponseSerializer,
    DiseaseDetectionRequestSerializer, DiseaseDetectionResponseSerializer,
    PestDetectionRequestSerializer, PestDetectionResponseSerializer,
    DroughtDetectionRequestSerializer, DroughtDetectionResponseSerializer,
    ReportCreateSerializer, ReportStatusUpdateSerializer, ReportListSerializer
)
import uuid
import random
from rest_framework_simplejwt.tokens import RefreshToken

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        full_name = request.data.get('fullName')
        role = request.data.get('role')
        city = request.data.get('city')
        state = request.data.get('state')
        gps_lat = request.data.get('gpsLat')
        gps_lng = request.data.get('gpsLng')
        
        if not all([phone, password, full_name, role]):
            return Response({
                'success': False,
                'message': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(phone=phone).exists():
            return Response({
                'success': False,
                'message': 'Phone number already registered'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.create(
                id=uuid.uuid4(),
                phone=phone,
                full_name=full_name,
                role=role,
                city=city,
                state=state,
                gps_lat=gps_lat,
                gps_lng=gps_lng
            )
            user.set_password(password)
            user.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'data': {
                    'userId': str(user.id),
                    'fullName': user.full_name,
                    'role': user.role,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        
        if not phone or not password:
            return Response({
                'success': False,
                'message': 'Phone and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(phone=phone)
            if not user.check_password(password):
                return Response({
                    'success': False,
                    'message': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'userId': str(user.id),
                    'fullName': user.full_name,
                    'role': user.role,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh)
                }
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

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
    serializer_class = ReportListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        'status', 'state', 'city',
        'plant_detection__plantId', 'disease_detection__diseaseId',
        'pest_detection__pestId', 'drought_detection__droughtLevel'
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('startDate')
        end_date = self.request.query_params.get('endDate')
        
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__gte=start_date)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__lte=end_date)
            except ValueError:
                pass
                
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = ReportCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            report = serializer.save()
            return Response({
                'success': True,
                'message': 'Report submitted successfully',
                'data': ReportListSerializer(report).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Failed to submit report',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': {
                'reports': serializer.data
            }
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })

class ReportStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Report not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ReportStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        report.status = serializer.validated_data['status']
        report.notes = serializer.validated_data.get('notes', '')
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.save()

        return Response({
            'success': True,
            'message': 'Report status updated successfully',
            'data': {
                'reportId': str(report.id),
                'status': report.status,
                'reviewedBy': str(report.reviewed_by.id),
                'reviewedAt': report.reviewed_at,
                'reviewNotes': report.notes
            }
        })

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

class PlantDetectionView(APIView):
    def post(self, request):
        # Validate request
        request_serializer = PlantDetectionRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': request_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Dummy detection logic - will be replaced with AI model later
        # For now, we'll just return a random plant type ID
        dummy_plant_types = [
            '550e8400-e29b-41d4-a716-446655440000',  # Tomato
            '550e8400-e29b-41d4-a716-446655440001',  # Potato
            '550e8400-e29b-41d4-a716-446655440002',  # Wheat
            '550e8400-e29b-41d4-a716-446655440003',  # Corn
        ]
        
        # Simulate detection with 90% confidence
        detected_plant_id = random.choice(dummy_plant_types)
        confidence = random.uniform(0.9, 1.0)

        return Response({
            'success': True,
            'data': {
                'plantId': detected_plant_id,
                'confidence': round(confidence, 2),
                'imageUrl': request_serializer.validated_data['image_url']
            }
        })

class DiseaseDetectionView(APIView):
    def post(self, request):
        serializer = DiseaseDetectionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Dummy disease detection logic
        dummy_diseases = [
            {
                'id': '550e8400-e29b-41d4-a716-446655440010',
                'name': 'Early Blight',
                'description': 'A fungal disease that affects tomatoes and potatoes, causing dark spots on leaves and stems.',
                'treatment': 'Remove infected leaves, apply fungicides, and practice crop rotation.',
                'plant_types': ['550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440001'],
                'severity': 'medium'
            },
            {
                'id': '550e8400-e29b-41d4-a716-446655440011',
                'name': 'Late Blight',
                'description': 'A devastating disease that can destroy entire tomato and potato crops.',
                'treatment': 'Apply fungicides preventatively, remove infected plants, and ensure good air circulation.',
                'plant_types': ['550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440001'],
                'severity': 'high'
            },
            {
                'id': '550e8400-e29b-41d4-a716-446655440012',
                'name': 'Rust',
                'description': 'A fungal disease that creates orange or brown spots on wheat leaves.',
                'treatment': 'Use resistant varieties, apply fungicides, and practice crop rotation.',
                'plant_types': ['550e8400-e29b-41d4-a716-446655440002'],
                'severity': 'medium'
            },
            {
                'id': '550e8400-e29b-41d4-a716-446655440013',
                'name': 'Gray Leaf Spot',
                'description': 'A fungal disease that affects corn, causing gray lesions on leaves.',
                'treatment': 'Use resistant hybrids, apply fungicides, and practice crop rotation.',
                'plant_types': ['550e8400-e29b-41d4-a716-446655440003'],
                'severity': 'medium'
            }
        ]
        
        # Simulate detection with random confidence
        detected_disease = random.choice(dummy_diseases)
        confidence = round(random.uniform(0.8, 1.0), 2)

        return Response({
            'success': True,
            'data': {
                'diseaseId': detected_disease['id'],
                'name': detected_disease['name'],
                'description': detected_disease['description'],
                'treatment': detected_disease['treatment'],
                'severity': detected_disease['severity'],
                'confidence': confidence,
                'imageUrl': serializer.validated_data['image_url']
            }
        })

class PestDetectionView(APIView):
    def post(self, request):
        serializer = PestDetectionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Dummy pest detection logic
        dummy_pests = [
            {
                'id': '550e8400-e29b-41d4-a716-446655440020',
                'name': 'Aphids',
                'description': 'Small, soft-bodied insects that feed on plant sap.',
                'treatment': 'Use insecticidal soap, neem oil, or introduce natural predators like ladybugs.',
                'severity': 'medium'
            },
            {
                'id': '550e8400-e29b-41d4-a716-446655440021',
                'name': 'Whiteflies',
                'description': 'Tiny white insects that feed on plant sap and spread diseases.',
                'treatment': 'Use yellow sticky traps, insecticidal soap, or neem oil.',
                'severity': 'high'
            },
            {
                'id': '550e8400-e29b-41d4-a716-446655440022',
                'name': 'Spider Mites',
                'description': 'Tiny arachnids that cause yellowing and webbing on leaves.',
                'treatment': 'Increase humidity, use miticides, or introduce predatory mites.',
                'severity': 'medium'
            },
            {
                'id': '550e8400-e29b-41d4-a716-446655440023',
                'name': 'Caterpillars',
                'description': 'Larvae of butterflies and moths that feed on leaves.',
                'treatment': 'Handpick, use Bacillus thuringiensis (Bt), or introduce natural predators.',
                'severity': 'low'
            }
        ]
        
        # Simulate detection with random confidence
        detected_pest = random.choice(dummy_pests)
        confidence = round(random.uniform(0.8, 1.0), 2)

        return Response({
            'success': True,
            'data': {
                'pestId': detected_pest['id'],
                'name': detected_pest['name'],
                'description': detected_pest['description'],
                'treatment': detected_pest['treatment'],
                'severity': detected_pest['severity'],
                'confidence': confidence,
                'imageUrl': serializer.validated_data['image_url']
            }
        })

class DroughtDetectionView(APIView):
    def post(self, request):
        serializer = DroughtDetectionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Dummy drought detection logic
        # Drought levels: 0 (no drought) to 5 (severe drought)
        drought_level = random.randint(0, 5)
        confidence = round(random.uniform(0.8, 1.0), 2)

        # Map drought levels to descriptions
        drought_descriptions = {
            0: "No drought - Soil moisture is optimal",
            1: "Mild drought - Slightly dry conditions",
            2: "Moderate drought - Soil is dry, plants may show stress",
            3: "Severe drought - Significant water stress",
            4: "Extreme drought - Critical water shortage",
            5: "Exceptional drought - Widespread water scarcity"
        }

        return Response({
            'success': True,
            'data': {
                'droughtLevel': drought_level,
                'description': drought_descriptions[drought_level],
                'confidence': confidence,
                'imageUrl': serializer.validated_data['image_url']
            }
        }) 