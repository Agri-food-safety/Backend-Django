from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login
from .models import User, PlantHealthReport, Alert
from .serializers import UserSerializer, PlantHealthReportSerializer, AlertSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({'status': 'success'})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

from django.db.models import Count
import math

class PlantHealthReportViewSet(viewsets.ModelViewSet):
    queryset = PlantHealthReport.objects.all()
    serializer_class = PlantHealthReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def geojson(self, request):
        reports = PlantHealthReport.objects.all()
        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [report.longitude, report.latitude]
                },
                "properties": {
                    "id": report.id,
                    "condition": report.condition,
                    "plant_type": report.plant_type
                }
            } for report in reports]
        }
        return Response(geojson)

    @action(detail=False, methods=['get'])
    def disease_distribution(self, request):
        condition_dist = PlantHealthReport.objects.values('condition').annotate(
            count=Count('id')
        ).order_by('-count')

        plant_dist = PlantHealthReport.objects.values('plant_type').annotate(
            count=Count('id')
        ).order_by('-count')

        return Response({
            'by_condition': condition_dist,
            'by_plant_type': plant_dist
        })

    @action(detail=False, methods=['get'])
    def nearby_reports(self, request):
        lat = float(request.query_params.get('lat', 0))
        lng = float(request.query_params.get('lng', 0))
        radius = float(request.query_params.get('radius', 10))  # km

        # Simple distance calculation (approximation)
        reports = []
        for report in PlantHealthReport.objects.all():
            distance = math.sqrt((report.latitude - lat)**2 + (report.longitude - lng)**2)
            if distance <= radius/111:  # Approx 111km per degree
                reports.append({
                    'report': self.get_serializer(report).data,
                    'distance_km': distance * 111
                })

        return Response(sorted(reports, key=lambda x: x['distance_km']))

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        location = request.query_params.get('location')
        alerts = Alert.objects.filter(affected_area__icontains=location)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
