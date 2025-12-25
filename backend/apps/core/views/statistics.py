"""
Reports and statistics API views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
from apps.users.models import User
from apps.bookings.models import Booking
from apps.tournaments.models import Tournament
from apps.courts.models import Court


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    try:
        # User statistics
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True, is_banned=False).count()
        banned_users = User.objects.filter(is_banned=True).count()
        
        # Court statistics
        total_courts = Court.objects.count()
        active_courts = Court.objects.filter(is_active=True).count()
        
        # Tournament statistics
        total_tournaments = Tournament.objects.count()
        active_tournaments = Tournament.objects.filter(status='registration_open').count()
        upcoming_tournaments = Tournament.objects.filter(
            start_date__gte=datetime.utcnow()
        ).count()
        
        # Booking statistics
        total_bookings = Booking.objects.count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()
        
        # Recent growth (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = User.objects.filter(created_at__gte=seven_days_ago).count()
        new_bookings_week = Booking.objects.filter(created_at__gte=seven_days_ago).count()
        
        return Response({
            'users': {
                'total': total_users,
                'active': active_users,
                'banned': banned_users,
                'new_this_week': new_users_week,
            },
            'courts': {
                'total': total_courts,
                'active': active_courts,
            },
            'tournaments': {
                'total': total_tournaments,
                'active': active_tournaments,
                'upcoming': upcoming_tournaments,
            },
            'bookings': {
                'total': total_bookings,
                'pending': pending_bookings,
                'confirmed': confirmed_bookings,
                'new_this_week': new_bookings_week,
            },
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_growth_chart(request):
    """Get user growth data for charts"""
    try:
        days = int(request.query_params.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Group users by date
        users = User.objects.filter(created_at__gte=start_date).order_by('created_at')
        
        # Count users per day
        data = []
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            count = User.objects.filter(
                created_at__gte=current_date,
                created_at__lt=next_date
            ).count()
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': count
            })
            current_date = next_date
        
        return Response({'data': data})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_stats_chart(request):
    """Get booking statistics for charts"""
    try:
        days = int(request.query_params.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Count bookings per day
        data = []
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            count = Booking.objects.filter(
                created_at__gte=current_date,
                created_at__lt=next_date
            ).count()
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': count
            })
            current_date = next_date
        
        return Response({'data': data})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def popular_courts(request):
    """Get most popular courts by booking count"""
    try:
        limit = int(request.query_params.get('limit', 10))
        
        # This is a simplified version - MongoDB aggregation would be better
        courts = Court.objects.filter(is_active=True)[:limit]
        
        data = []
        for court in courts:
            booking_count = Booking.objects.filter(court=court).count()
            data.append({
                'id': str(court.id),
                'name': court.name_i18n.get('tk', court.name_i18n.get('ru', court.name_i18n.get('en', 'Unknown'))),
                'booking_count': booking_count,
            })
        
        # Sort by booking count
        data.sort(key=lambda x: x['booking_count'], reverse=True)
        
        return Response({'data': data[:limit]})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

