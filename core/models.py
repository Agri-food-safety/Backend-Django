import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None  # Remove username field
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=20, choices=[
        ('farmer', 'Farmer'),
        ('inspector', 'Inspector')
    ])
    full_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    gps_lat = models.FloatField()
    gps_lng = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name', 'role', 'city', 'state', 'gps_lat', 'gps_lng']

    objects = UserManager()

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

class PlantType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100)
    common_diseases = models.JSONField(default=list)

    def __str__(self):
        return f"{self.name} ({self.scientific_name})"

class DiseaseType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    arabic_name = models.CharField(max_length=100, null=True, blank=True)
    tag = models.CharField(max_length=100)
    description = models.TextField()
    treatment = models.TextField()
    plant_types = models.JSONField(default=list)
    severity = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ])

    def __str__(self):
        return self.name

class PestType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    treatment = models.TextField()
    plant_types = models.JSONField(default=list)
    severity = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ])

    def __str__(self):
        return self.name

class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    plant_type = models.ForeignKey(PlantType, on_delete=models.CASCADE, null=True, blank=True)
    image_url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)
    gps_lat = models.FloatField()
    gps_lng = models.FloatField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    
    # Detection results
    plant_detection = models.JSONField(null=True, blank=True)
    disease_detection = models.JSONField(null=True, blank=True)
    pest_detection = models.JSONField(null=True, blank=True)
    drought_detection = models.JSONField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=[
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed')
    ], default='submitted')
    notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report {self.id} by {self.user.full_name}"

class Alert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=[
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('danger', 'Danger')
    ])
    target_state = models.CharField(max_length=100)
    target_city = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_alerts')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.title
