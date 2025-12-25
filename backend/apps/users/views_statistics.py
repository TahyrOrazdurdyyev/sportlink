"""
User Statistics - Advanced Analytics
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.users.models import User
from apps.bookings.models import Booking
from apps.tournaments.models import Tournament
from apps.subscriptions.permissions import require_feature
from datetime import datetime, timedelta
from collections import defaultdict


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@require_feature('advanced_statistics')
def user_statistics(request, user_id=None):
    """
    Get comprehensive user statistics
    
    Includes:
    - Booking history
    - Tournament participation
    - Match history
    - Activity patterns
    - Performance metrics
    """
    # Get user
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
    else:
        user = request.user
    
    # Time range
    time_range = request.query_params.get('range', '30')  # days
    start_date = datetime.utcnow() - timedelta(days=int(time_range))
    
    # Booking statistics
    bookings = Booking.objects(user=user, created_at__gte=start_date)
    total_bookings = bookings.count()
    confirmed_bookings = bookings.filter(status='confirmed').count()
    cancelled_bookings = bookings.filter(status='cancelled').count()
    completed_bookings = bookings.filter(status='completed').count()
    
    # Total hours played
    total_hours = sum([b.duration_hours() for b in completed_bookings])
    
    # Total spent
    total_spent = sum([float(b.total_price) for b in bookings if b.total_price])
    
    # Most frequent courts
    court_frequency = defaultdict(int)
    for booking in bookings:
        if booking.court:
            court_frequency[str(booking.court.id)] += 1
    
    # Tournaments
    all_tournaments = Tournament.objects()
    participated_tournaments = []
    for tournament in all_tournaments:
        for participant in tournament.participants:
            if str(participant.user_id) == str(user.id):
                participated_tournaments.append({
                    'id': str(tournament.id),
                    'name': tournament.name,
                    'start_date': tournament.start_date.isoformat() if tournament.start_date else None,
                    'status': tournament.status,
                })
                break
    
    # Activity by day of week
    day_of_week_stats = defaultdict(int)
    for booking in completed_bookings:
        if booking.start_time:
            day_name = booking.start_time.strftime('%A')
            day_of_week_stats[day_name] += 1
    
    # Activity by hour
    hour_of_day_stats = defaultdict(int)
    for booking in completed_bookings:
        if booking.start_time:
            hour = booking.start_time.hour
            hour_of_day_stats[hour] += 1
    
    # Recent activity
    recent_bookings = list(bookings.order_by('-created_at')[:10])
    recent_activity = []
    for booking in recent_bookings:
        recent_activity.append({
            'id': str(booking.id),
            'court_name': booking.court.name if booking.court else 'Unknown',
            'start_time': booking.start_time.isoformat() if booking.start_time else None,
            'status': booking.status,
            'created_at': booking.created_at.isoformat(),
        })
    
    # Performance metrics
    performance = {
        'average_bookings_per_week': round(total_bookings / (int(time_range) / 7), 1),
        'completion_rate': round((completed_bookings / total_bookings * 100), 1) if total_bookings > 0 else 0,
        'cancellation_rate': round((cancelled_bookings / total_bookings * 100), 1) if total_bookings > 0 else 0,
    }
    
    return Response({
        'user': {
            'id': str(user.id),
            'name': user.get_full_name(),
            'experience_level': user.experience_level,
            'rating': float(user.rating) if user.rating else 0.0,
        },
        'time_range': {
            'days': int(time_range),
            'start_date': start_date.isoformat(),
        },
        'bookings': {
            'total': total_bookings,
            'confirmed': confirmed_bookings,
            'cancelled': cancelled_bookings,
            'completed': completed_bookings,
            'total_hours': round(total_hours, 1),
            'total_spent': round(total_spent, 2),
        },
        'tournaments': {
            'total_participated': len(participated_tournaments),
            'list': participated_tournaments,
        },
        'activity_patterns': {
            'by_day_of_week': dict(day_of_week_stats),
            'by_hour_of_day': dict(hour_of_day_stats),
        },
        'performance': performance,
        'recent_activity': recent_activity,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@require_feature('advanced_statistics')
def user_achievements(request):
    """
    Get user achievements and milestones
    """
    user = request.user
    
    # Calculate achievements
    total_bookings = Booking.objects(user=user).count()
    completed_bookings = Booking.objects(user=user, status='completed').count()
    
    all_tournaments = Tournament.objects()
    tournaments_count = 0
    for tournament in all_tournaments:
        for participant in tournament.participants:
            if str(participant.user_id) == str(user.id):
                tournaments_count += 1
                break
    
    achievements = []
    
    # Booking milestones
    if completed_bookings >= 1:
        achievements.append({
            'id': 'first_booking',
            'name': 'First Booking',
            'description': 'Completed your first booking',
            'icon': '🎾',
            'unlocked': True,
        })
    
    if completed_bookings >= 10:
        achievements.append({
            'id': 'regular_player',
            'name': 'Regular Player',
            'description': 'Completed 10 bookings',
            'icon': '🏆',
            'unlocked': True,
        })
    
    if completed_bookings >= 50:
        achievements.append({
            'id': 'veteran_player',
            'name': 'Veteran Player',
            'description': 'Completed 50 bookings',
            'icon': '⭐',
            'unlocked': True,
        })
    
    # Tournament participation
    if tournaments_count >= 1:
        achievements.append({
            'id': 'tournament_debut',
            'name': 'Tournament Debut',
            'description': 'Participated in your first tournament',
            'icon': '🏅',
            'unlocked': True,
        })
    
    # Experience level
    if user.experience_level and user.experience_level >= 5:
        achievements.append({
            'id': 'advanced_player',
            'name': 'Advanced Player',
            'description': 'Reached experience level 5',
            'icon': '🌟',
            'unlocked': True,
        })
    
    return Response({
        'total_achievements': len(achievements),
        'achievements': achievements,
        'stats': {
            'completed_bookings': completed_bookings,
            'tournaments_participated': tournaments_count,
            'experience_level': user.experience_level or 1,
            'rating': float(user.rating) if user.rating else 0.0,
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_leaderboard(request):
    """
    Get leaderboard rankings
    """
    # Get top users by rating
    top_by_rating = User.objects(
        is_active=True,
        rating__gte=0.1
    ).order_by('-rating')[:10]
    
    # Get top users by bookings
    from collections import Counter
    booking_counts = Counter()
    for booking in Booking.objects(status='completed'):
        booking_counts[str(booking.user.id)] += 1
    
    top_bookers = []
    for user_id, count in booking_counts.most_common(10):
        try:
            user = User.objects.get(id=user_id)
            top_bookers.append({
                'id': str(user.id),
                'name': user.get_full_name(),
                'count': count,
            })
        except:
            pass
    
    return Response({
        'leaderboards': {
            'by_rating': [
                {
                    'rank': idx + 1,
                    'id': str(user.id),
                    'name': user.get_full_name(),
                    'rating': float(user.rating) if user.rating else 0.0,
                    'experience_level': user.experience_level,
                } for idx, user in enumerate(top_by_rating)
            ],
            'by_bookings': [
                {
                    'rank': idx + 1,
                    **user_data
                } for idx, user_data in enumerate(top_bookers)
            ],
        }
    })

