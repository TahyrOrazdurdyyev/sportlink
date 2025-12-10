"""
Notification tasks for MongoDB
"""
from celery import shared_task
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_booking_confirmation(self, booking_id):
    """Send booking confirmation notification"""
    try:
        from apps.bookings.models import Booking
        from apps.notifications.models import Notification
        
        booking = Booking.objects.get(id=booking_id)
        user = booking.user
        
        # Create notification
        notification = Notification(
            user=user,
            type='push',
            event_type='booking_confirmed',
            title='Booking Confirmed',
            title_i18n={
                'tk': 'Rezerwasiya tassyklandy',
                'ru': 'Бронирование подтверждено', 
                'en': 'Booking Confirmed'
            },
            message=f'Your booking at {booking.court.get_name()} is confirmed',
            message_i18n={
                'tk': f'{booking.court.get_name()} meýdanyndaky rezerwasiyanyňyz tassyklandy',
                'ru': f'Ваше бронирование на {booking.court.get_name()} подтверждено',
                'en': f'Your booking at {booking.court.get_name()} is confirmed'
            },
            payload={
                'booking_id': str(booking.id),
                'court_name': booking.court.get_name(),
                'start_time': booking.start_time.isoformat(),
                'end_time': booking.end_time.isoformat()
            }
        )
        notification.save()
        
        logger.info(f"Booking confirmation notification created for booking {booking_id}")
        return f"Notification sent for booking {booking_id}"
        
    except Exception as exc:
        logger.error(f"Failed to send booking confirmation for {booking_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_tournament_notification(self, tournament_id):
    """Send tournament notification to relevant users"""
    try:
        from apps.tournaments.models import Tournament
        from apps.notifications.models import Notification
        from apps.users.models import User
        
        tournament = Tournament.objects.get(id=tournament_id)
        
        # Find users interested in tournaments (simplified)
        users = User.objects.filter(
            is_active=True,
            goals__contains='tournament_info'
        )[:100]  # Limit to 100 users
        
        notifications = []
        for user in users:
            notification = Notification(
                user=user,
                type='push',
                event_type='tournament_created',
                title='New Tournament Available',
                title_i18n={
                    'tk': 'Täze ýaryş döredildi',
                    'ru': 'Создан новый турнир',
                    'en': 'New Tournament Available'
                },
                message=f'{tournament.get_name()} - Register now!',
                payload={
                    'tournament_id': str(tournament.id),
                    'tournament_name': tournament.get_name(),
                    'start_date': tournament.start_date.isoformat()
                }
            )
            notifications.append(notification)
        
        # Bulk create notifications
        for notification in notifications:
            notification.save()
        
        logger.info(f"Tournament notification sent to {len(notifications)} users")
        return f"Tournament notification sent to {len(notifications)} users"
        
    except Exception as exc:
        logger.error(f"Failed to send tournament notification for {tournament_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_old_notifications():
    """Clean up old notifications"""
    try:
        from apps.notifications.models import Notification
        from datetime import datetime, timedelta
        
        # Delete notifications older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_notifications = Notification.objects.filter(created_at__lt=cutoff_date)
        count = old_notifications.count()
        old_notifications.delete()
        
        logger.info(f"Cleaned up {count} old notifications")
        return f"Cleaned up {count} old notifications"
        
    except Exception as exc:
        logger.error(f"Failed to cleanup notifications: {exc}")
        raise exc


@shared_task
def send_booking_reminder():
    """Send booking reminders for tomorrow's bookings"""
    try:
        from apps.bookings.models import Booking
        from apps.notifications.models import Notification
        from datetime import datetime, timedelta
        
        # Find bookings for tomorrow
        tomorrow = datetime.utcnow() + timedelta(days=1)
        tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = tomorrow.replace(hour=23, minute=59, second=59)
        
        bookings = Booking.objects.filter(
            start_time__gte=tomorrow_start,
            start_time__lte=tomorrow_end,
            status='confirmed'
        )
        
        notifications = []
        for booking in bookings:
            notification = Notification(
                user=booking.user,
                type='push',
                event_type='booking_reminder',
                title='Booking Reminder',
                title_i18n={
                    'tk': 'Rezerwasiya ýatlatmasy',
                    'ru': 'Напоминание о бронировании',
                    'en': 'Booking Reminder'
                },
                message=f'You have a booking tomorrow at {booking.court.get_name()}',
                payload={
                    'booking_id': str(booking.id),
                    'court_name': booking.court.get_name(),
                    'start_time': booking.start_time.isoformat()
                }
            )
            notifications.append(notification)
        
        # Save notifications
        for notification in notifications:
            notification.save()
        
        logger.info(f"Sent {len(notifications)} booking reminders")
        return f"Sent {len(notifications)} booking reminders"
        
    except Exception as exc:
        logger.error(f"Failed to send booking reminders: {exc}")
        raise exc