from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime
from .models import User, PlantType, DiseaseType, Report, Alert, PestType
from .serializers import (
    UserSerializer, PlantTypeSerializer, DiseaseTypeSerializer,
    ReportSerializer, AlertSerializer, UserRegistrationSerializer,
    UserLoginSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    PlantDetectionRequestSerializer, PlantDetectionResponseSerializer,
    DiseaseDetectionRequestSerializer, DiseaseDetectionResponseSerializer,
    PestDetectionRequestSerializer, PestDetectionResponseSerializer,
    DroughtDetectionRequestSerializer, DroughtDetectionResponseSerializer,
    ReportCreateSerializer, ReportStatusUpdateSerializer, ReportListSerializer,
    PestTypeSerializer
)
import uuid
import random
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from .detection import detect_plant, detect_disease


class UserRegistrationView(APIView):
    """
    Register a new user.
    
    Accepts POST request with the following fields:
    - phone: User's phone number
    - password: User's password
    - fullName: User's full name
    - role: User's role (farmer/expert)
    - city: User's city (optional)
    - state: User's state (optional)
    - gpsLat: User's latitude (optional)
    - gpsLng: User's longitude (optional)
    
    Returns:
    - success: Boolean indicating if registration was successful
    - message: Description of the result
    - data: User information and tokens if successful
    """
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
    """
    Authenticate a user and return JWT tokens.
    
    Accepts POST request with the following fields:
    - phone: User's phone number
    - password: User's password
    
    Returns:
    - success: Boolean indicating if login was successful
    - message: Description of the result
    - data: User information and tokens if successful
    """
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
                    'phone': user.phone,
                    'fullName': user.full_name,
                    'role': user.role,
                    'city': user.city,
                    'state': user.state,
                    'gpsLat': user.gps_lat,
                    'gpsLng': user.gps_lng,
                    'createdAt': user.created_at,
                    'lastActive': user.last_active,
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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['severity']
    search_fields = ['name', 'description']

class PestTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing pest types.
    
    Supports the following operations:
    - GET /api/pest-types/: List all pest types
    - POST /api/pest-types/: Create a new pest type
    - GET /api/pest-types/{id}/: Retrieve a specific pest type
    - PUT /api/pest-types/{id}/: Update a specific pest type
    - DELETE /api/pest-types/{id}/: Delete a specific pest type
    """
    queryset = PestType.objects.all()
    serializer_class = PestTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['severity']
    search_fields = ['name', 'description']

class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing reports.
    
    Supports the following operations:
    - GET /api/reports/: List all reports
    - POST /api/reports/: Create a new report
    - GET /api/reports/{id}/: Retrieve a specific report
    - PUT /api/reports/{id}/: Update a specific report
    - DELETE /api/reports/{id}/: Delete a specific report
    - GET /api/reports/user/{user_id}/: Get reports for a specific user
    
    Report fields:
    - gpsLat: GPS latitude
    - gpsLng: GPS longitude
    - city: City name
    - state: State name
    - imageUrl: URL of the plant image
    - plantType: Plant type information
    - disease: Disease information
    - pest: Pest information
    - drought: Drought information
    - notes: Additional notes
    """
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
        
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def user_reports(self, request, user_id=None):
        """
        Get reports for a specific user.
        
        Permission rules:
        - Farmers can only view their own reports
        - Experts can view any user's reports
        """
        try:
            # Check if the requested user exists
            target_user = User.objects.get(id=user_id)
            
            # Get the current user
            current_user = request.user
            
            # Check permissions
            if current_user.role == 'farmer' and str(current_user.id) != user_id:
                return Response({
                    'success': False,
                    'message': 'You can only view your own reports'
                }, status=status.HTTP_403_FORBIDDEN)
                
            # Get reports for the target user
            reports = Report.objects.filter(user=target_user)
            
            # Apply date filters if provided
            start_date = request.query_params.get('startDate')
            end_date = request.query_params.get('endDate')
            
            if start_date:
                try:
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    reports = reports.filter(timestamp__gte=start_date)
                except ValueError:
                    pass
                    
            if end_date:
                try:
                    end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    reports = reports.filter(timestamp__lte=end_date)
                except ValueError:
                    pass
            
            # Serialize the reports
            serializer = ReportListSerializer(reports, many=True)
            
            return Response({
                'success': True,
                'data': {
                    'userId': user_id,
                    'userName': target_user.full_name,
                    'reports': serializer.data
                }
            })
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['severity', 'target_state', 'target_city']
    search_fields = ['title', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get query parameters
        state = self.request.query_params.get('state')
        city = self.request.query_params.get('city')
        severity = self.request.query_params.get('severity')
        start_date = self.request.query_params.get('startDate')
        end_date = self.request.query_params.get('endDate')
        
        # Apply region filters
        if state:
            queryset = queryset.filter(target_state=state)
            
        if city:
            queryset = queryset.filter(target_city=city)
            
        # Apply severity filter
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Apply date range filters - only consider day, month, year
        if start_date:
            try:
                # Parse the date string to extract year, month, day
                start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                # Create a date object with only year, month, day
                start_date_only = start_date_obj.date()
                # Filter alerts created on or after this date
                queryset = queryset.filter(created_at__date__gte=start_date_only)
            except ValueError:
                pass
                
        if end_date:
            try:
                # Parse the date string to extract year, month, day
                end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                # Create a date object with only year, month, day
                end_date_only = end_date_obj.date()
                # Filter alerts created on or before this date
                queryset = queryset.filter(expires_at__date__lte=end_date_only)
            except ValueError:
                pass
                
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        # Get filter parameters for response metadata
        state = request.query_params.get('state')
        city = request.query_params.get('city')
        severity = request.query_params.get('severity')
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        
        return Response({
            'success': True,
            'data': {
                'filters': {
                    'state': state,
                    'city': city,
                    'severity': severity,
                    'startDate': start_date,
                    'endDate': end_date
                },
                'alerts': serializer.data
            }
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def by_region(self, request):
        """
        Get alerts for a specific region (state and/or city).
        
        Query Parameters:
        - state: State name (required)
        - city: City name (optional)
        - severity: Filter by severity level (optional)
        - startDate: Filter by start date (optional)
        - endDate: Filter by end date (optional)
        
        Returns:
        - success: Boolean indicating if the request was successful
        - data: List of alerts matching the region criteria
        """
        state = request.query_params.get('state')
        city = request.query_params.get('city')
        severity = request.query_params.get('severity')
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        
        if not state:
            return Response({
                'success': False,
                'message': 'State parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Start with base queryset
        queryset = self.get_queryset().filter(target_state=state)
        
        # Add city filter if provided
        if city:
            queryset = queryset.filter(target_city=city)
            
        # Add severity filter if provided
        if severity:
            queryset = queryset.filter(severity=severity)
            
        # Apply date range filters - only consider day, month, year
        if start_date:
            try:
                # Parse the date string to extract year, month, day
                start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                # Create a date object with only year, month, day
                start_date_only = start_date_obj.date()
                # Filter alerts created on or after this date
                queryset = queryset.filter(created_at__date__gte=start_date_only)
            except ValueError:
                pass
                
        if end_date:
            try:
                # Parse the date string to extract year, month, day
                end_date_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                # Create a date object with only year, month, day
                end_date_only = end_date_obj.date()
                # Filter alerts created on or before this date
                queryset = queryset.filter(created_at__date__lte=end_date_only)
            except ValueError:
                pass
            
        # Serialize the results
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'data': {
                'state': state,
                'city': city,
                'alerts': serializer.data
            }
        })

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response({
            'success': True,
            'data': serializer.data
        })
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
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PlantDetectionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Get a random plant type
        plant_types = PlantType.objects.all()
        plant_type = random.choice(list(plant_types))
        confidence = round(random.uniform(0.85, 0.99), 2)
        
        # Ensure proper encoding of Arabic text
        response_data = {
            'success': True,
            'data': {
                'plantId': str(plant_type.id),
                'name': plant_type.name.encode('utf-8').decode('utf-8'),
                'scientificName': plant_type.scientific_name.encode('utf-8').decode('utf-8'),
                'confidence': confidence,
                'imageUrl': serializer.validated_data['image_url']
            }
        }
        
        return Response(response_data, content_type='application/json; charset=utf-8')

class DiseaseDetectionView(APIView):
    """
    Detect plant diseases from an image.
    
    Accepts POST request with:
    - imageUrl: URL of the plant image
    
    Returns:
    - success: Boolean indicating if detection was successful
    - data: Disease detection results including:
        - diseaseId: Unique identifier for the disease
        - name: Disease name
        - description: Disease description
        - treatment: Treatment recommendations
        - confidence: Detection confidence score
    """
    def post(self, request):
        serializer = DiseaseDetectionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get a random disease type
        diseases = DiseaseType.objects.all()
        disease_type = random.choice(list(diseases))
        confidence = round(random.uniform(0.85, 0.99), 2)
        
        # Ensure proper encoding of Arabic text
        response_data = {
            'success': True,
            'data': {
                'diseaseId': str(disease_type.id),
                'name': disease_type.name.encode('utf-8').decode('utf-8'),
                'description': disease_type.description.encode('utf-8').decode('utf-8'),
                'treatment': disease_type.treatment.encode('utf-8').decode('utf-8'),
                'severity': disease_type.severity,
                'confidence': confidence,
                'imageUrl': serializer.validated_data['image_url']
            }
        }
        
        return Response(response_data, content_type='application/json; charset=utf-8')

class PestDetectionView(APIView):
    """
    Detect plant pests from an image.
    
    Accepts POST request with:
    - imageUrl: URL of the plant image
    
    Returns:
    - success: Boolean indicating if detection was successful
    - data: Pest detection results including:
        - pestId: Unique identifier for the pest
        - name: Pest name
        - confidence: Detection confidence score
    """
    def post(self, request):
        serializer = PestDetectionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get all pests from database
        pests = PestType.objects.all()
        
        # Convert to list of dictionaries with same structure as before
        pest_list = [{
            'id': str(pest.id),
            'name': pest.name.encode('utf-8').decode('utf-8'),
            'description': pest.description.encode('utf-8').decode('utf-8'),
            'treatment': pest.treatment.encode('utf-8').decode('utf-8'),
            'severity': pest.severity
        } for pest in pests]
        
        # Simulate detection with random confidence
        detected_pest = random.choice(pest_list)
        confidence = round(random.uniform(0.8, 1.0), 2)

        response_data = {
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
        }
        
        return Response(response_data, content_type='application/json; charset=utf-8')

class DroughtDetectionView(APIView):
    """
    Detect drought conditions from an image.
    
    Accepts POST request with:
    - imageUrl: URL of the plant/field image
    
    Returns:
    - success: Boolean indicating if detection was successful
    - data: Drought detection results including:
        - droughtLevel: Level of drought (0-5)
        - description: Description of drought conditions
        - confidence: Detection confidence score
    """
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

        # Map drought levels to descriptions in English and Arabic
        drought_descriptions = {
            0: {
                'en': "No drought - Soil moisture is optimal",
                'ar': "لا يوجد جفاف - رطوبة التربة مثالية"
            },
            1: {
                'en': "Mild drought - Slightly dry conditions",
                'ar': "جفاف خفيف - ظروف جافة قليلاً"
            },
            2: {
                'en': "Moderate drought - Soil is dry, plants may show stress",
                'ar': "جفاف معتدل - التربة جافة، قد تظهر النباتات علامات الإجهاد"
            },
            3: {
                'en': "Severe drought - Significant water stress",
                'ar': "جفاف شديد - إجهاد مائي كبير"
            },
            4: {
                'en': "Extreme drought - Critical water shortage",
                'ar': "جفاف متطرف - نقص حاد في المياه"
            },
            5: {
                'en': "Exceptional drought - Widespread water scarcity",
                'ar': "جفاف استثنائي - ندرة المياه منتشرة"
            }
        }

        response_data = {
            'success': True,
            'data': {
                'droughtLevel': drought_level,
                'description':
                    drought_descriptions[drought_level]['ar'],
                'confidence': confidence,
                'imageUrl': serializer.validated_data['image_url']
            }
        }
        
        return Response(response_data, content_type='application/json; charset=utf-8') 