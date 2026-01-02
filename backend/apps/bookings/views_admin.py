"""
Admin views for booking management
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from apps.bookings.models import Booking
from apps.bookings.serializers import BookingSerializer


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_bookings(request):
    """
    Get all bookings with filters for admin panel
    """
    try:
        # Get query parameters
        court_id = request.GET.get('court')
        user_id = request.GET.get('user')
        status_filter = request.GET.get('status')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Build query
        query = {}
        if court_id:
            query['court'] = court_id
        if user_id:
            query['user'] = user_id
        if status_filter:
            query['status'] = status_filter
        if start_date and end_date:
            from dateutil import parser
            query['start_time__gte'] = parser.parse(start_date)
            query['start_time__lte'] = parser.parse(end_date)
        
        # Get bookings
        bookings = Booking.objects(**query).order_by('-created_at')
        
        # Serialize
        bookings_data = []
        for booking in bookings:
            booking_dict = {
                'id': str(booking.id),
                'court_id': str(booking.court.id) if booking.court else None,
                'court_name': booking.court.name_i18n if booking.court else None,
                'user_id': str(booking.user.id) if booking.user else None,
                'user_phone': booking.user.phone if booking.user else None,
                'user_name': f"{booking.user.first_name or ''} {booking.user.last_name or ''}".strip() if booking.user else None,
                'start_time': booking.start_time.isoformat() if booking.start_time else None,
                'end_time': booking.end_time.isoformat() if booking.end_time else None,
                'duration_hours': (booking.end_time - booking.start_time).total_seconds() / 3600 if booking.start_time and booking.end_time else 0,
                'status': booking.status,
                'payment_status': booking.payment_status,
                'total_price': float(booking.total_price) if booking.total_price else 0,
                'equipment_rental': booking.equipment_rental,
                'equipment_quantity': booking.equipment_quantity,
                'find_opponents': booking.find_opponents,
                'opponents_needed': booking.opponents_needed,
                'created_at': booking.created_at.isoformat() if booking.created_at else None,
            }
            bookings_data.append(booking_dict)
        
        return Response({
            'bookings': bookings_data,
            'total': len(bookings_data)
        })
        
    except Exception as e:
        print(f"Error listing bookings: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_booking_statistics(request):
    """
    Get booking statistics for admin dashboard
    """
    try:
        from datetime import datetime, timedelta
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        stats = {
            'total_bookings': Booking.objects.count(),
            'today_bookings': Booking.objects(start_time__gte=today).count(),
            'week_bookings': Booking.objects(start_time__gte=week_ago).count(),
            'month_bookings': Booking.objects(start_time__gte=month_ago).count(),
            'pending_bookings': Booking.objects(status='pending').count(),
            'confirmed_bookings': Booking.objects(status='confirmed').count(),
            'cancelled_bookings': Booking.objects(status='cancelled').count(),
            'completed_bookings': Booking.objects(status='completed').count(),
        }
        
        return Response(stats)
        
    except Exception as e:
        print(f"Error getting booking statistics: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

