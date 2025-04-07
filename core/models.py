from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class UserType(models.TextChoices):
        FARMER = 'FR', _('Farmer')
        INSPECTOR = 'IN', _('Inspector')
        ADMIN = 'AD', _('Admin')

    user_type = models.CharField(
        max_length=2,
        choices=UserType.choices,
        default=UserType.FARMER,
    )
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=255, blank=True)

class PlantHealthReport(models.Model):
    class ConditionType(models.TextChoices):
        DISEASE = 'DS', _('Disease')
        DROUGHT = 'DR', _('Drought')
        PEST = 'PE', _('Pest')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='reports/')
    plant_type = models.CharField(max_length=100, blank=True)
    condition = models.CharField(max_length=2, choices=ConditionType.choices)
    condition_details = models.TextField()
    diagnosis = models.TextField()
    treatment_advice = models.TextField()
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

class Alert(models.Model):
    class Severity(models.TextChoices):
        DANGER = 'DG', _('Danger')
        WARNING = 'WN', _('Warning')
        INFO = 'IF', _('Information')

    title = models.CharField(max_length=255)
    message = models.TextField()
    severity = models.CharField(max_length=2, choices=Severity.choices)
    affected_area = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
