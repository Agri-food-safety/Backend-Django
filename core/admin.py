from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PlantHealthReport, Alert

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone_number', 'location')
    list_filter = ('user_type',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional info', {'fields': ('user_type', 'location')}),
    )

class PlantHealthReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'plant_type', 'get_condition_display', 'created_at')
    list_filter = ('condition', 'created_at')
    search_fields = ('user__username', 'plant_type', 'condition_details')
    date_hierarchy = 'created_at'

class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_severity_display', 'affected_area', 'created_at')
    list_filter = ('severity', 'created_at')
    search_fields = ('title', 'message', 'affected_area')
    date_hierarchy = 'created_at'

admin.site.register(User, CustomUserAdmin)
admin.site.register(PlantHealthReport, PlantHealthReportAdmin)
admin.site.register(Alert, AlertAdmin)
