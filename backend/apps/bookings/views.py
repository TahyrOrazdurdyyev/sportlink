"""
Booking views for MongoDB
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.mongoengine_drf import MongoEngineModelViewSet
from apps.bookings.models import Booking
from apps.bookings.serializers import (
    BookingSerializer, BookingCreateSerializer, BookingListSerializer
)
from apps.bookings.validators import BookingValidator, check_time_slot_conflict
from apps.courts.models import Court
from datetime import datetime
from dateutil import parser


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
    
    def create(self, request, *args, **kwargs):
        """Create booking with conflict check and tariff validation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        court_id = request.data.get('court')
        start_time = parser.parse(request.data.get('start_time'))
        end_time = parser.parse(request.data.get('end_time'))
        equipment_needed = request.data.get('equipment_needed', False)
        
        # Validate subscription and tariff limits
        validator = BookingValidator(request.user, start_time, end_time)
        if not validator.validate():
            return Response({
                'error': 'Booking validation failed',
                'validation': validator.get_validation_result()
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check equipment rental feature
        if equipment_needed:
            if not validator.subscription:
                return Response({
                    'error': 'No active subscription',
                    'detail': 'You need an active subscription to rent equipment'
                }, status=status.HTTP_403_FORBIDDEN)
            
            plan = validator.subscription.plan
            if not plan.features.get('equipment_rental', False):
                return Response({
                    'error': 'Equipment rental not available',
                    'detail': 'Your subscription plan does not include equipment rental',
                    'feature': 'equipment_rental'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Check for time slot conflicts
        try:
            court = Court.objects.get(id=court_id)
        except Court.DoesNotExist:
            return Response({'error': 'Court not found'}, status=status.HTTP_404_NOT_FOUND)
        
        conflict_check = check_time_slot_conflict(court, start_time, end_time)
        if conflict_check['has_conflict']:
            return Response({
                'error': 'Time slot already booked',
                'detail': 'This court is already booked for the selected time',
                'conflicts': conflict_check['conflicts']
            }, status=status.HTTP_409_CONFLICT)
        
        # Create booking
        booking = serializer.save(user=request.user)
        
        # Try to auto-match opponents if requested
        matches = []
        if booking.find_opponents and booking.opponents_needed > 0:
            from apps.bookings.matching import auto_match_opponents
            from apps.notifications.services import notify_opponent_matched, notify_seeker_matched
            
            matches = auto_match_opponents(booking)
            
            # Send notifications for each match
            for match in matches:
                # Notify the opponent
                notify_opponent_matched(booking, match.opponent)
                # Notify the seeker
                notify_seeker_matched(booking, match.opponent)
        
        response_data = BookingSerializer(booking).data
        if matches:
            response_data['matches_found'] = len(matches)
            response_data['matched_opponents'] = [
                {
                    'id': str(match.opponent.id),
                    'nickname': match.opponent.nickname,
                    'first_name': match.opponent.first_name,
                    'last_name': match.opponent.last_name,
                }
                for match in matches
            ]
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_availability(request):
    """Check court availability and tariff restrictions for specific time slot"""
    from apps.users.models import UserSubscription
    from datetime import timedelta
    
    court_id = request.query_params.get('court_id')
    start_time_str = request.query_params.get('start_time')
    end_time_str = request.query_params.get('end_time')
    
    if not all([court_id, start_time_str, end_time_str]):
        return Response({
            'error': 'Missing parameters',
            'required': ['court_id', 'start_time', 'end_time']
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        court = Court.objects.get(id=court_id)
        start_time = parser.parse(start_time_str)
        end_time = parser.parse(end_time_str)
    except Court.DoesNotExist:
        return Response({'error': 'Court not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Invalid parameters: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate duration in hours
    duration_hours = (end_time - start_time).total_seconds() / 3600
    day_of_week = start_time.isoweekday()
    
    # Initialize validation results
    validation_results = {
        'time_slot_available': True,
        'tariff_valid': True,
        'can_book': True,
        'errors': [],
        'warnings': []
    }
    
    # Check user's subscription
    user_subscription = UserSubscription.objects(
        user=request.user,
        status='active',
        end_date__gte=datetime.now()
    ).first()
    
    if not user_subscription:
        validation_results['tariff_valid'] = False
        validation_results['can_book'] = False
        validation_results['errors'].append({
            'code': 'NO_SUBSCRIPTION',
            'message': 'No active subscription found'
        })
    else:
        plan = user_subscription.plan
        booking_limits = plan.booking_limits or {}
        
        # Check court booking feature
        if not plan.features.get('court_booking', False):
            validation_results['tariff_valid'] = False
            validation_results['can_book'] = False
            validation_results['errors'].append({
                'code': 'FEATURE_NOT_AVAILABLE',
                'message': 'Your subscription does not include court booking'
            })
        
        # Check day of week
        allowed_days = booking_limits.get('allowed_days', [])
        if allowed_days and day_of_week not in allowed_days:
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            allowed_day_names = [day_names[d-1] for d in allowed_days]
            validation_results['tariff_valid'] = False
            validation_results['can_book'] = False
            validation_results['errors'].append({
                'code': 'DAY_NOT_ALLOWED',
                'message': f'Booking only allowed on: {", ".join(allowed_day_names)}',
                'allowed_days': allowed_days,
                'requested_day': day_of_week
            })
        
        # Check duration
        max_duration = booking_limits.get('max_duration_hours', 0)
        if max_duration > 0 and duration_hours > max_duration:
            validation_results['tariff_valid'] = False
            validation_results['can_book'] = False
            validation_results['errors'].append({
                'code': 'DURATION_EXCEEDS_LIMIT',
                'message': f'Maximum booking duration is {max_duration} hours',
                'max_duration_hours': max_duration,
                'requested_duration_hours': duration_hours
            })
        
        # Check weekly limit
        bookings_per_week = booking_limits.get('bookings_per_week', 0)
        if bookings_per_week > 0:
            week_start = start_time - timedelta(days=start_time.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)
            
            weekly_bookings = Booking.objects(
                user=request.user,
                status__in=['confirmed', 'pending'],
                start_time__gte=week_start,
                start_time__lt=week_end
            ).count()
            
            if weekly_bookings >= bookings_per_week:
                validation_results['tariff_valid'] = False
                validation_results['can_book'] = False
                validation_results['errors'].append({
                    'code': 'WEEKLY_LIMIT_REACHED',
                    'message': f'Weekly booking limit ({bookings_per_week}) reached',
                    'bookings_per_week': bookings_per_week,
                    'current_week_bookings': weekly_bookings
                })
            elif weekly_bookings >= bookings_per_week - 1:
                validation_results['warnings'].append({
                    'code': 'WEEKLY_LIMIT_NEAR',
                    'message': f'This will be your last booking this week ({weekly_bookings + 1}/{bookings_per_week})'
                })
    
    # Check for time slot conflicts
    conflicts = Booking.objects(
        court=court,
        status__in=['confirmed', 'pending'],
        start_time__lt=end_time,
        end_time__gt=start_time
    )
    
    conflicting_bookings = []
    if conflicts.count() > 0:
        validation_results['time_slot_available'] = False
        validation_results['can_book'] = False
        for booking in conflicts:
            conflicting_bookings.append({
                'id': str(booking.id),
                'start_time': booking.start_time.isoformat(),
                'end_time': booking.end_time.isoformat(),
                'status': booking.status,
            })
        validation_results['errors'].append({
            'code': 'TIME_SLOT_OCCUPIED',
            'message': 'This time slot is already booked',
            'conflicts': conflicting_bookings
        })
    
    return Response({
        'available': validation_results['can_book'],
        'validation': validation_results,
        'court_id': str(court.id),
        'court_name': court.name,
        'requested_start': start_time.isoformat(),
        'requested_end': end_time.isoformat(),
        'duration_hours': duration_hours,
        'day_of_week': day_of_week,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def confirm_booking(request, booking_id):
    """Confirm a booking (admin only)"""
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    
    booking.confirm()
    
    return Response({'message': 'Booking confirmed successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_weekly_limits(request):
    """Get user's weekly booking limits and current usage"""
    from apps.users.models import UserSubscription
    
    # Get user's active subscription
    user_subscription = UserSubscription.objects(
        user=request.user,
        status='active',
        end_date__gte=datetime.now()
    ).first()
    
    if not user_subscription:
        return Response({
            'has_subscription': False,
            'message': 'No active subscription found'
        })
    
    plan = user_subscription.plan
    booking_limits = plan.booking_limits or {}
    bookings_per_week = booking_limits.get('bookings_per_week', 0)
    
    # Get current calendar week
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    next_week_start = week_end
    
    # Get user's bookings in current week
    weekly_bookings_query = Booking.objects(
        user=request.user,
        status__in=['confirmed', 'pending'],
        start_time__gte=week_start,
        start_time__lt=week_end
    ).order_by('start_time')
    
    weekly_bookings_count = weekly_bookings_query.count()
    
    bookings_list = []
    for booking in weekly_bookings_query:
        bookings_list.append({
            'id': str(booking.id),
            'court_id': str(booking.court.id) if booking.court else None,
            'court_name': booking.court.name if booking.court else 'Unknown',
            'start_time': booking.start_time.isoformat(),
            'end_time': booking.end_time.isoformat(),
            'status': booking.status,
            'duration_hours': (booking.end_time - booking.start_time).total_seconds() / 3600
        })
    
    unlimited = bookings_per_week == 0
    limit_reached = not unlimited and weekly_bookings_count >= bookings_per_week
    
    result = {
        'has_subscription': True,
        'plan_name': plan.name,
        'unlimited': unlimited,
        'bookings_per_week': bookings_per_week,
        'current_week_bookings': weekly_bookings_count,
        'remaining_bookings': None if unlimited else max(0, bookings_per_week - weekly_bookings_count),
        'limit_reached': limit_reached,
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat(),
        'next_week_start': next_week_start.isoformat(),
        'days_until_next_week': (next_week_start - now).days,
        'bookings': bookings_list,
        'other_limits': {
            'max_duration_hours': booking_limits.get('max_duration_hours', 0),
            'allowed_days': booking_limits.get('allowed_days', [])
        }
    }
    
    return Response(result)


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