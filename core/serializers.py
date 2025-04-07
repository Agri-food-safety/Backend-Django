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
        fields = ['id', 'user', 'plant_type', 'image_url', 'timestamp',
                 'gps_lat', 'gps_lng', 'city', 'state', 'detection_result',
                 'confidence_score', 'status', 'notes', 'reviewed_by',
                 'reviewed_at']
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