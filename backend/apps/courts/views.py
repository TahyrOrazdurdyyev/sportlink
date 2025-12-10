"""
Court views for MongoDB
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.mongoengine_drf import MongoEngineModelViewSet, GeoQueryMixin
from apps.courts.models import Court
from apps.courts.serializers import (
    CourtSerializer, CourtListSerializer, CourtDetailSerializer
)


class CourtViewSet(MongoEngineModelViewSet, GeoQueryMixin):
    """Court search and details (read-only for users)"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Court.objects.filter(is_active=True)
        
        # Filter by type
        court_type = self.request.query_params.get('type')
        if court_type:
            queryset = queryset.filter(type=court_type)
        
        # Filter by location and radius
        lat = self.request.query_params.get('lat', type=float)
        lng = self.request.query_params.get('lng', type=float)
        radius_km = self.request.query_params.get('radius_km', type=float, default=10.0)
        
        if lat and lng:
            queryset = self.filter_by_location(queryset, lat, lng, radius_km)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourtDetailSerializer
        return CourtListSerializer
    
    def list(self, request, *args, **kwargs):
        """List courts with distance calculation"""
        queryset = self.get_queryset()
        
        # Get user location for distance calculation
        lat = request.query_params.get('lat', type=float)
        lng = request.query_params.get('lng', type=float)
        
        courts = list(queryset[:100])  # Limit results
        
        # Calculate distances
        if lat and lng:
            for court in courts:
                if court.location:
                    court._distance = self.calculate_distance(
                        court.location, [lng, lat]
                    )
                else:
                    court._distance = None
            
            # Sort by distance
            courts.sort(key=lambda c: c._distance or 999999)
        
        serializer = self.get_serializer(courts, many=True)
        return Response(serializer.data)


# Admin court views
class AdminCourtViewSet(MongoEngineModelViewSet):
    """Admin court CRUD"""
    serializer_class = CourtSerializer
    permission_classes = [IsAuthenticated]  # Should be IsAdminUser
    
    def get_queryset(self):
        return Court.objects.all()
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)


@api_view(['GET'])
def court_availability(request, court_id):
    """Get court availability for specific date"""
    try:
        court = Court.objects.get(id=court_id)
    except Court.DoesNotExist:
        return Response({'error': 'Court not found'}, status=status.HTTP_404_NOT_FOUND)
    
    date_str = request.query_params.get('date')
    if not date_str:
        return Response({'error': 'Date parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from datetime import datetime
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        slots = court.get_availability_for_date(date)
        
        availability = [
            {
                'start_time': slot.start_time.isoformat(),
                'end_time': slot.end_time.isoformat(),
                'status': slot.status,
                'booking_id': str(slot.booking_id) if slot.booking_id else None
            }
            for slot in slots
        ]
        
        return Response({'availability': availability})
        
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                       status=status.HTTP_400_BAD_REQUEST)
