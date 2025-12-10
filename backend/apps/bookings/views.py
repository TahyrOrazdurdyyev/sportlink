"""
Booking views for MongoDB
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.mongoengine_drf import MongoEngineModelViewSet
from apps.bookings.models import Booking
from apps.bookings.serializers import (
    BookingSerializer, BookingCreateSerializer, BookingListSerializer
)
from apps.courts.models import Court


class BookingViewSet(MongoEngineModelViewSet):
    """Booking CRUD operations"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own bookings
        return Booking.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'list':
            return BookingListSerializer
        return BookingSerializer
    
    def perform_create(self, serializer):
        """Create booking with validation"""
        # Set user to current user
        booking_data = serializer.validated_data
        booking_data['user'] = self.request.user
        
        # Validate court availability
        court = booking_data['court']
        start_time = booking_data['start_time']
        end_time = booking_data['end_time']
        
        if not court.is_available(start_time, end_time):
            return Response(
                {'error': 'Court is not available for the selected time'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create booking
        booking = serializer.save()
        
        return booking


@api_view(['POST'])
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not booking.can_cancel():
        return Response(
            {'error': 'Booking cannot be cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    reason = request.data.get('reason', '')
    booking.cancel(reason)
    
    return Response({'message': 'Booking cancelled successfully'})


@api_view(['POST'])
def confirm_booking(request, booking_id):
    """Confirm a booking (admin only)"""
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    
    booking.confirm()
    
    return Response({'message': 'Booking confirmed successfully'})


class UserBookingsView(APIView):
    """Get user's bookings with filtering"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        queryset = Booking.objects.filter(user=request.user)
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Order by start time
        bookings = list(queryset.order_by('-start_time')[:50])
        
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)