from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, PlantType, DiseaseType, Report, Alert

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    fullName = serializers.CharField(source='full_name')
    gpsLat = serializers.FloatField(source='gps_lat')
    gpsLng = serializers.FloatField(source='gps_lng')

    class Meta:
        model = User
        fields = ['phone', 'password', 'fullName', 'role', 'city', 'state', 'gpsLat', 'gpsLng']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            phone=validated_data['phone'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            role=validated_data['role'],
            city=validated_data['city'],
            state=validated_data['state'],
            gps_lat=validated_data['gps_lat'],
            gps_lng=validated_data['gps_lng']
        )
        return user

class UserLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['success'] = True
        data['data'] = {
            'userId': str(self.user.id),
            'phone': self.user.phone,
            'fullName': self.user.full_name,
            'role': self.user.role
        }
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'full_name', 'city', 'state', 
                 'gps_lat', 'gps_lng', 'created_at', 'last_active']
        read_only_fields = ['created_at', 'last_active']

class PlantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantType
        fields = ['id', 'name', 'scientific_name', 'common_diseases']

class DiseaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiseaseType
        fields = ['id', 'name', 'description', 'treatment', 
                 'plant_types', 'severity']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            'id', 'user', 'plant_type', 'image_url', 'timestamp',
            'gps_lat', 'gps_lng', 'city', 'state',
            'plant_detection', 'disease_detection', 'pest_detection', 'drought_detection',
            'status', 'notes', 'reviewed_by', 'reviewed_at'
        ]
        read_only_fields = ['timestamp', 'reviewed_at']

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'title', 'description', 'severity', 'target_state',
                 'target_city', 'created_by', 'created_at', 'expires_at']
        read_only_fields = ['created_at']

class UserProfileSerializer(serializers.ModelSerializer):
    userId = serializers.UUIDField(source='id')
    fullName = serializers.CharField(source='full_name')
    gpsLat = serializers.FloatField(source='gps_lat')
    gpsLng = serializers.FloatField(source='gps_lng')
    createdAt = serializers.DateTimeField(source='created_at')
    lastActive = serializers.DateTimeField(source='last_active')

    class Meta:
        model = User
        fields = ['userId', 'phone', 'fullName', 'role', 'city', 'state', 
                 'gpsLat', 'gpsLng', 'createdAt', 'lastActive']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source='full_name', required=False)
    gpsLat = serializers.FloatField(source='gps_lat', required=False)
    gpsLng = serializers.FloatField(source='gps_lng', required=False)

    class Meta:
        model = User
        fields = ['fullName', 'city', 'state', 'gpsLat', 'gpsLng']

    def update(self, instance, validated_data):
        if 'full_name' in validated_data:
            instance.full_name = validated_data['full_name']
        if 'city' in validated_data:
            instance.city = validated_data['city']
        if 'state' in validated_data:
            instance.state = validated_data['state']
        if 'gps_lat' in validated_data:
            instance.gps_lat = validated_data['gps_lat']
        if 'gps_lng' in validated_data:
            instance.gps_lng = validated_data['gps_lng']
        
        instance.save()
        return instance

class PlantDetectionRequestSerializer(serializers.Serializer):
    image_url = serializers.URLField()

class PlantDetectionResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    data = serializers.JSONField()
    message = serializers.CharField(required=False)

class DiseaseDetectionRequestSerializer(serializers.Serializer):
    image_url = serializers.URLField()

class DiseaseDetectionResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    data = serializers.JSONField()
    message = serializers.CharField(required=False)

class PestDetectionRequestSerializer(serializers.Serializer):
    image_url = serializers.URLField()

class PestDetectionResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    data = serializers.JSONField()
    message = serializers.CharField(required=False)

class DroughtDetectionRequestSerializer(serializers.Serializer):
    image_url = serializers.URLField()

class DroughtDetectionResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    data = serializers.JSONField()
    message = serializers.CharField(required=False)

class ReportCreateSerializer(serializers.ModelSerializer):
    gpsLat = serializers.FloatField(source='gps_lat')
    gpsLng = serializers.FloatField(source='gps_lng')
    imageUrl = serializers.URLField(source='image_url')
    plantType = serializers.JSONField(source='plant_detection')
    disease = serializers.JSONField(source='disease_detection')
    pest = serializers.JSONField(source='pest_detection')
    drought = serializers.JSONField(source='drought_detection')

    class Meta:
        model = Report
        fields = [
            'gpsLat', 'gpsLng', 'city', 'state', 'notes',
            'imageUrl', 'plantType', 'disease', 'pest', 'drought'
        ]

    def create(self, validated_data):
        # Extract detection data
        plant_detection = validated_data.pop('plant_detection', None)
        disease_detection = validated_data.pop('disease_detection', None)
        pest_detection = validated_data.pop('pest_detection', None)
        drought_detection = validated_data.pop('drought_detection', None)

        # Create report
        report = Report.objects.create(
            user=self.context['request'].user,
            plant_detection=plant_detection,
            disease_detection=disease_detection,
            pest_detection=pest_detection,
            drought_detection=drought_detection,
            **validated_data
        )

        # Set plant_type if plant detection was successful
        if plant_detection and plant_detection.get('plantId'):
            try:
                plant_type = PlantType.objects.get(id=plant_detection['plantId'])
                report.plant_type = plant_type
                report.save()
            except PlantType.DoesNotExist:
                pass

        return report

class ReportStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['submitted', 'reviewed'])
    reviewNotes = serializers.CharField(source='notes', required=False)

class ReportListSerializer(serializers.ModelSerializer):
    reportId = serializers.UUIDField(source='id')
    gpsLat = serializers.FloatField(source='gps_lat')
    gpsLng = serializers.FloatField(source='gps_lng')
    imageUrl = serializers.URLField(source='image_url')
    reviewedBy = serializers.UUIDField(source='reviewed_by.id', allow_null=True)
    reviewedAt = serializers.DateTimeField(source='reviewed_at', allow_null=True)
    reviewNotes = serializers.CharField(source='notes', allow_null=True)

    class Meta:
        model = Report
        fields = [
            'reportId', 'status', 'gpsLat', 'gpsLng', 'city', 'state',
            'imageUrl', 'plant_detection', 'disease_detection',
            'pest_detection', 'drought_detection', 'reviewedBy',
            'reviewedAt', 'reviewNotes', 'timestamp'
        ] 