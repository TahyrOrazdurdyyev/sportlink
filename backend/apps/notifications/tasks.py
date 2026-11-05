"""
Celery tasks for sending notifications
"""
from celery import shared_task
from apps.users.models import User
from .fcm_utils import (
    send_push_notification,
    send_push_notification_multicast,
    notify_booking_confirmed,
    notify_tournament_reminder,
    notify_match_invitation,
)
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_booking_confirmation_notification(user_id: str, booking_id: str, court_name: str, time: str):
    """Send booking confirmation notification"""
    try:
        user = User.objects.get(id=user_id)
        if user.fcm_token:
            notify_booking_confirmed(
                user_token=user.fcm_token,
                booking_id=booking_id,
                court_name=court_name,
                time=time,
            )
            logger.info(f'Sent booking confirmation to user {user_id}')
        else:
            logger.warning(f'User {user_id} has no FCM token')
    except User.DoesNotExist:
        logger.error(f'User {user_id} not found')
    except Exception as e:
        logger.error(f'Error sending booking notification: {e}')


@shared_task
def send_tournament_reminder_notification(tournament_id: str, hours_before: int):
    """Send tournament reminder to all participants"""
    try:
        from apps.tournaments.models import Tournament
        
        tournament = Tournament.objects.get(id=tournament_id)
        participant_ids = [p.user_id for p in tournament.participants]
        
        # Get users with FCM tokens
        users = User.objects.filter(id__in=participant_ids, fcm_token__exists=True, fcm_token__ne='')
        tokens = [user.fcm_token for user in users]
        
        if tokens:
            result = send_push_notification_multicast(
                tokens=tokens,
                title='Турнир скоро начнется',
                body=f'{tournament.name} начнется через {hours_before} часов',
                data={
                    'type': 'tournament_reminder',
                    'tournament_id': str(tournament_id),
                },
            )
            logger.info(f'Sent tournament reminder: {result}')
        else:
            logger.warning(f'No users with FCM tokens for tournament {tournament_id}')
            
    except Exception as e:
        logger.error(f'Error sending tournament reminder: {e}')


@shared_task
def send_match_invitation_notification(user_id: str, match_id: str, inviter_name: str):
    """Send match invitation notification"""
    try:
        user = User.objects.get(id=user_id)
        if user.fcm_token:
            notify_match_invitation(
                user_token=user.fcm_token,
                match_id=match_id,
                inviter_name=inviter_name,
            )
            logger.info(f'Sent match invitation to user {user_id}')
        else:
            logger.warning(f'User {user_id} has no FCM token')
    except User.DoesNotExist:
        logger.error(f'User {user_id} not found')
    except Exception as e:
        logger.error(f'Error sending match invitation: {e}')


@shared_task
def send_custom_notification(user_id: str, title: str, body: str, data: dict = None):
    """Send custom notification to a user"""
    try:
        user = User.objects.get(id=user_id)
        if user.fcm_token:
            send_push_notification(
                token=user.fcm_token,
                title=title,
                body=body,
                data=data or {},
            )
            logger.info(f'Sent custom notification to user {user_id}')
        else:
            logger.warning(f'User {user_id} has no FCM token')
    except User.DoesNotExist:
        logger.error(f'User {user_id} not found')
    except Exception as e:
        logger.error(f'Error sending custom notification: {e}')


@shared_task
def send_broadcast_notification(title: str, body: str, data: dict = None, user_ids: list = None):
    """Send notification to multiple users or all active users"""
    try:
        # Get users
        if user_ids:
            users = User.objects.filter(id__in=user_ids, fcm_token__exists=True, fcm_token__ne='')
        else:
            users = User.objects.filter(is_active=True, fcm_token__exists=True, fcm_token__ne='')
        
        tokens = [user.fcm_token for user in users]
        
        if not tokens:
            logger.warning('No users with FCM tokens found')
            return
        
        # Send in batches of 500 (FCM limit)
        batch_size = 500
        total_success = 0
        total_failure = 0
        
        for i in range(0, len(tokens), batch_size):
            batch_tokens = tokens[i:i + batch_size]
            result = send_push_notification_multicast(
                tokens=batch_tokens,
                title=title,
                body=body,
                data=data or {},
            )
            total_success += result['success']
            total_failure += result['failure']
        
        logger.info(f'Broadcast notification sent: {total_success} success, {total_failure} failure')
        
    except Exception as e:
        logger.error(f'Error sending broadcast notification: {e}')
