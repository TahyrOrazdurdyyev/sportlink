"""
Firebase Cloud Messaging (FCM) utilities for sending push notifications
"""
from firebase_admin import messaging
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def send_push_notification(
    token: str,
    title: str,
    body: str,
    data: Optional[Dict[str, str]] = None,
    image_url: Optional[str] = None,
) -> bool:
    """
    Send push notification to a single device
    
    Args:
        token: FCM device token
        title: Notification title
        body: Notification body
        data: Additional data payload
        image_url: Optional image URL
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image_url,
        )
        
        android_config = messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                sound='default',
                color='#FF5722',
            ),
        )
        
        apns_config = messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='default',
                    badge=1,
                ),
            ),
        )
        
        message = messaging.Message(
            notification=notification,
            data=data or {},
            token=token,
            android=android_config,
            apns=apns_config,
        )
        
        response = messaging.send(message)
        logger.info(f'Successfully sent message: {response}')
        return True
        
    except Exception as e:
        logger.error(f'Error sending push notification: {e}')
        return False


def send_push_notification_multicast(
    tokens: List[str],
    title: str,
    body: str,
    data: Optional[Dict[str, str]] = None,
    image_url: Optional[str] = None,
) -> Dict[str, int]:
    """
    Send push notification to multiple devices
    
    Args:
        tokens: List of FCM device tokens (max 500)
        title: Notification title
        body: Notification body
        data: Additional data payload
        image_url: Optional image URL
        
    Returns:
        dict: {'success': count, 'failure': count}
    """
    try:
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image_url,
        )
        
        android_config = messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                sound='default',
                color='#FF5722',
            ),
        )
        
        apns_config = messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='default',
                    badge=1,
                ),
            ),
        )
        
        message = messaging.MulticastMessage(
            notification=notification,
            data=data or {},
            tokens=tokens[:500],  # FCM limit
            android=android_config,
            apns=apns_config,
        )
        
        response = messaging.send_multicast(message)
        logger.info(f'Successfully sent {response.success_count} messages')
        logger.info(f'Failed to send {response.failure_count} messages')
        
        return {
            'success': response.success_count,
            'failure': response.failure_count,
        }
        
    except Exception as e:
        logger.error(f'Error sending multicast push notification: {e}')
        return {'success': 0, 'failure': len(tokens)}


def send_push_to_topic(
    topic: str,
    title: str,
    body: str,
    data: Optional[Dict[str, str]] = None,
    image_url: Optional[str] = None,
) -> bool:
    """
    Send push notification to a topic (all subscribed devices)
    
    Args:
        topic: Topic name
        title: Notification title
        body: Notification body
        data: Additional data payload
        image_url: Optional image URL
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image_url,
        )
        
        android_config = messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                sound='default',
                color='#FF5722',
            ),
        )
        
        apns_config = messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='default',
                    badge=1,
                ),
            ),
        )
        
        message = messaging.Message(
            notification=notification,
            data=data or {},
            topic=topic,
            android=android_config,
            apns=apns_config,
        )
        
        response = messaging.send(message)
        logger.info(f'Successfully sent message to topic {topic}: {response}')
        return True
        
    except Exception as e:
        logger.error(f'Error sending push notification to topic {topic}: {e}')
        return False


# Helper functions for common notification types

def notify_booking_confirmed(user_token: str, booking_id: str, court_name: str, time: str) -> bool:
    """Notify user about confirmed booking"""
    return send_push_notification(
        token=user_token,
        title='Бронирование подтверждено',
        body=f'Ваше бронирование на {court_name} в {time} подтверждено',
        data={
            'type': 'booking_confirmed',
            'booking_id': booking_id,
        },
    )


def notify_tournament_reminder(user_token: str, tournament_id: str, tournament_name: str, hours_left: int) -> bool:
    """Notify user about upcoming tournament"""
    return send_push_notification(
        token=user_token,
        title='Турнир скоро начнется',
        body=f'{tournament_name} начнется через {hours_left} часов',
        data={
            'type': 'tournament_reminder',
            'tournament_id': tournament_id,
        },
    )


def notify_match_invitation(user_token: str, match_id: str, inviter_name: str) -> bool:
    """Notify user about match invitation"""
    return send_push_notification(
        token=user_token,
        title='Приглашение на матч',
        body=f'{inviter_name} приглашает вас на матч',
        data={
            'type': 'match_invitation',
            'match_id': match_id,
        },
    )


def notify_new_message(user_token: str, sender_name: str, message_preview: str) -> bool:
    """Notify user about new message"""
    return send_push_notification(
        token=user_token,
        title=f'Сообщение от {sender_name}',
        body=message_preview,
        data={
            'type': 'new_message',
        },
    )

