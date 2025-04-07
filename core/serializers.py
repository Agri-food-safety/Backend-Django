from rest_framework import serializers
from .models import User, PlantHealthReport, Alert

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'phone_number', 'location']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            user_type=validated_data.get('user_type', 'FR'),
            phone_number=validated_data.get('phone_number', ''),
            location=validated_data.get('location', '')
        )
        return user

class PlantHealthReportSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()

    def get_location(self, obj):
        return {
            'latitude': obj.latitude,
            'longitude': obj.longitude
        }

    class Meta:
        model = PlantHealthReport
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']
