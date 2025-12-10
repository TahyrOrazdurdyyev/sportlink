"""
Admin court views
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.gis.geos import Point
from ..models import Court, Tariff, AvailabilitySlot
from ..serializers import CourtSerializer, TariffSerializer
from apps.core.permissions import IsAdminUser as IsAdmin


class AdminCourtViewSet(viewsets.ModelViewSet):
    """
    Admin Court CRUD
    """
    queryset = Court.objects.all()
    serializer_class = CourtSerializer
    permission_classes = [IsAdmin]
    
    def create(self, request):
        """Create court"""
        data = request.data.copy()
        
        # Handle location
        location = data.get('location')
        if location and isinstance(location, list) and len(location) == 2:
            data['location'] = Point(location[0], location[1], srid=4326)
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AdminTariffViewSet(viewsets.ModelViewSet):
    """
    Admin Tariff CRUD
    """
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    permission_classes = [IsAdmin]

