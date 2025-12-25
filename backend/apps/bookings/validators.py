"""
Booking validation utilities
"""
from datetime import datetime, timedelta
from apps.subscriptions.models_user import UserSubscription
from apps.bookings.models import Booking


class BookingValidator:
    """Validator for booking requests against subscription limits"""
    
    def __init__(self, user, start_time, end_time):
        self.user = user
        self.start_time = start_time
        self.end_time = end_time
        self.duration_hours = (end_time - start_time).total_seconds() / 3600
        self.day_of_week = start_time.isoweekday()
        self.errors = []
        self.warnings = []
        
    def validate(self):
        """Run all validation checks"""
        self._check_subscription()
        if self.subscription:
            self._check_feature_access()
            self._check_day_restriction()
            self._check_duration_limit()
            self._check_weekly_limit()
        
        return len(self.errors) == 0
    
    def _check_subscription(self):
        """Check if user has active subscription"""
        self.subscription = UserSubscription.objects(
            user=self.user,
            status='active',
            end_date__gte=datetime.now()
        ).first()
        
        if not self.subscription:
            self.errors.append({
                'code': 'NO_SUBSCRIPTION',
                'message': 'No active subscription found',
                'field': 'subscription'
            })
    
    def _check_feature_access(self):
        """Check if subscription includes court booking"""
        if not self.subscription.plan.features.get('court_booking', False):
            self.errors.append({
                'code': 'FEATURE_NOT_AVAILABLE',
                'message': 'Your subscription does not include court booking',
                'field': 'subscription'
            })
    
    def _check_day_restriction(self):
        """Check if booking day is allowed by subscription"""
        booking_limits = self.subscription.plan.booking_limits or {}
        allowed_days = booking_limits.get('allowed_days', [])
        
        if allowed_days and self.day_of_week not in allowed_days:
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            allowed_day_names = [day_names[d-1] for d in allowed_days]
            self.errors.append({
                'code': 'DAY_NOT_ALLOWED',
                'message': f'Booking only allowed on: {", ".join(allowed_day_names)}',
                'field': 'start_time',
                'allowed_days': allowed_days,
                'requested_day': self.day_of_week,
                'requested_day_name': day_names[self.day_of_week - 1]
            })
    
    def _check_duration_limit(self):
        """Check if booking duration exceeds subscription limit"""
        booking_limits = self.subscription.plan.booking_limits or {}
        max_duration = booking_limits.get('max_duration_hours', 0)
        
        if max_duration > 0 and self.duration_hours > max_duration:
            self.errors.append({
                'code': 'DURATION_EXCEEDS_LIMIT',
                'message': f'Maximum booking duration is {max_duration} hours. You requested {self.duration_hours} hours',
                'field': 'duration',
                'max_duration_hours': max_duration,
                'requested_duration_hours': self.duration_hours
            })
    
    def _check_weekly_limit(self):
        """Check if user has reached weekly booking limit (calendar week: Monday-Sunday)"""
        booking_limits = self.subscription.plan.booking_limits or {}
        bookings_per_week = booking_limits.get('bookings_per_week', 0)
        
        if bookings_per_week > 0:
            # Get start of CALENDAR WEEK (Monday 00:00:00)
            # If today is Monday (weekday=0), week_start is today
            # If today is Friday (weekday=4), week_start is 4 days ago (Monday)
            week_start = self.start_time - timedelta(days=self.start_time.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Week ends on Sunday 23:59:59
            week_end = week_start + timedelta(days=7)
            
            # Calculate next week start (next Monday 00:00:00)
            next_week_start = week_end
            
            # Count user's bookings in current calendar week
            weekly_bookings = Booking.objects(
                user=self.user,
                status__in=['confirmed', 'pending'],
                start_time__gte=week_start,
                start_time__lt=week_end
            ).count()
            
            # Get last booking date in current week for better error message
            last_booking = Booking.objects(
                user=self.user,
                status__in=['confirmed', 'pending'],
                start_time__gte=week_start,
                start_time__lt=week_end
            ).order_by('-start_time').first()
            
            if weekly_bookings >= bookings_per_week:
                # Calculate days until next Monday
                days_until_next_week = (next_week_start - self.start_time).days
                
                error_msg = f'Weekly booking limit ({bookings_per_week}) reached. You have {weekly_bookings} booking(s) this week'
                
                if last_booking:
                    last_booking_day = last_booking.start_time.strftime('%A, %B %d')
                    error_msg += f'. Last booking was on {last_booking_day}'
                
                if days_until_next_week > 0:
                    error_msg += f'. Next booking available from {next_week_start.strftime("%A, %B %d")} (in {days_until_next_week} day(s))'
                else:
                    error_msg += f'. Next booking available from next Monday'
                
                self.errors.append({
                    'code': 'WEEKLY_LIMIT_REACHED',
                    'message': error_msg,
                    'field': 'weekly_limit',
                    'bookings_per_week': bookings_per_week,
                    'current_week_bookings': weekly_bookings,
                    'current_week_start': week_start.isoformat(),
                    'current_week_end': week_end.isoformat(),
                    'next_available_date': next_week_start.isoformat(),
                    'days_until_available': days_until_next_week,
                    'last_booking_date': last_booking.start_time.isoformat() if last_booking else None
                })
            elif weekly_bookings >= bookings_per_week - 1:
                self.warnings.append({
                    'code': 'WEEKLY_LIMIT_NEAR',
                    'message': f'This will be your last booking this week ({weekly_bookings + 1}/{bookings_per_week}). Next booking available from {next_week_start.strftime("%A, %B %d")}',
                    'next_available_date': next_week_start.isoformat()
                })
    
    def get_validation_result(self):
        """Get validation result dictionary"""
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'duration_hours': self.duration_hours,
            'day_of_week': self.day_of_week
        }
    
    def get_weekly_booking_info(self):
        """Get detailed information about user's weekly bookings"""
        if not self.subscription:
            return None
        
        booking_limits = self.subscription.plan.booking_limits or {}
        bookings_per_week = booking_limits.get('bookings_per_week', 0)
        
        if bookings_per_week == 0:
            return {
                'unlimited': True,
                'bookings_per_week': 0,
                'current_week_bookings': 0,
                'remaining_bookings': None
            }
        
        # Get current calendar week
        week_start = self.start_time - timedelta(days=self.start_time.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)
        
        # Get user's bookings in current week
        weekly_bookings_query = Booking.objects(
            user=self.user,
            status__in=['confirmed', 'pending'],
            start_time__gte=week_start,
            start_time__lt=week_end
        ).order_by('start_time')
        
        weekly_bookings_count = weekly_bookings_query.count()
        
        bookings_list = []
        for booking in weekly_bookings_query:
            bookings_list.append({
                'id': str(booking.id),
                'court_name': booking.court.name if booking.court else 'Unknown',
                'start_time': booking.start_time.isoformat(),
                'end_time': booking.end_time.isoformat(),
                'status': booking.status
            })
        
        return {
            'unlimited': False,
            'bookings_per_week': bookings_per_week,
            'current_week_bookings': weekly_bookings_count,
            'remaining_bookings': max(0, bookings_per_week - weekly_bookings_count),
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'bookings': bookings_list,
            'limit_reached': weekly_bookings_count >= bookings_per_week
        }


def check_time_slot_conflict(court, start_time, end_time, exclude_booking_id=None):
    """Check if time slot has conflicts with existing bookings"""
    query = {
        'court': court,
        'status__in': ['confirmed', 'pending'],
        'start_time__lt': end_time,
        'end_time__gt': start_time
    }
    
    if exclude_booking_id:
        query['id__ne'] = exclude_booking_id
    
    conflicts = Booking.objects(**query)
    
    conflicting_bookings = []
    for booking in conflicts:
        conflicting_bookings.append({
            'id': str(booking.id),
            'start_time': booking.start_time.isoformat(),
            'end_time': booking.end_time.isoformat(),
            'status': booking.status,
        })
    
    return {
        'has_conflict': conflicts.count() > 0,
        'conflicts': conflicting_bookings
    }

