"""
Notification services
"""
from datetime import datetime
from apps.notifications.models import Notification, PushToken


def create_notification(user, notification_type, title_i18n, message_i18n, data=None):
    """
    Create a notification for a user.
    
    Args:
        user: User object
        notification_type: Type of notification (from Notification.TYPE_CHOICES)
        title_i18n: Dict with translations {'en': '...', 'ru': '...', 'tk': '...'}
        message_i18n: Dict with translations {'en': '...', 'ru': '...', 'tk': '...'}
        data: Optional dict with additional data
    
    Returns:
        Notification object
    """
    notification = Notification(
        user=user,
        type=notification_type,
        title=title_i18n,
        message=message_i18n,
        data=data or {}
    )
    notification.save()
    
    # TODO: Send push notification if user has tokens
    send_push_notification(notification)
    
    return notification


def send_push_notification(notification):
    """
    Send push notification to user's devices via Firebase Cloud Messaging.
    """
    # Get user's active push tokens
    tokens = PushToken.objects(user=notification.user, is_active=True)
    
    if not tokens:
        return
    
    # Get user's preferred language (default to 'en')
    user_language = getattr(notification.user, 'preferred_language', 'en')
    if user_language not in ['en', 'ru', 'tk']:
        user_language = 'en'
    
    # Get localized title and message
    title = notification.title.get(user_language, notification.title.get('en', ''))
    message = notification.message.get(user_language, notification.message.get('en', ''))
    
    # Send to each device
    for token in tokens:
        try:
            success = send_to_fcm(token.token, title, message, notification.data)
            
            if success:
                token.last_used_at = datetime.utcnow()
                token.save()
            else:
                # Deactivate invalid token
                token.is_active = False
                token.save()
        except Exception as e:
            # Log error
            print(f"Failed to send push notification: {e}")
            # Optionally deactivate invalid tokens
            token.is_active = False
            token.save()
    
    notification.mark_as_sent()


def send_to_fcm(token, title, body, data):
    """
    Send push notification via Firebase Cloud Messaging.
    
    Args:
        token: FCM device token
        title: Notification title
        body: Notification body
        data: Additional data payload
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import firebase_admin
        from firebase_admin import messaging, credentials
        
        # Initialize Firebase Admin SDK if not already initialized
        if not firebase_admin._apps:
            # Load credentials from environment or file
            import os
            from django.conf import settings
            
            # Try multiple paths
            possible_paths = [
                os.environ.get('FIREBASE_CREDENTIALS_PATH'),
                os.path.join(settings.BASE_DIR, 'config', 'firebase-adminsdk.json'),
                os.path.join(settings.BASE_DIR, 'firebase-credentials.json'),
                'config/firebase-adminsdk.json',
                'firebase-credentials.json',
            ]
            
            cred_path = None
            for path in possible_paths:
                if path and os.path.exists(path):
                    cred_path = path
                    break
            
            if cred_path:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print(f"Firebase initialized with credentials from: {cred_path}")
            else:
                print("Firebase credentials not found. Push notifications disabled.")
                print(f"Searched paths: {[p for p in possible_paths if p]}")
                return False
        
        # Prepare data payload (convert all values to strings)
        data_payload = {k: str(v) for k, v in (data or {}).items()}
        
        # Create message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data_payload,
            token=token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    sound='default',
                    color='#4CAF50',
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        badge=1,
                    ),
                ),
            ),
        )
        
        # Send message
        response = messaging.send(message)
        print(f"Successfully sent message: {response}")
        return True
        
    except ImportError:
        print("Firebase Admin SDK not installed. Install with: pip install firebase-admin")
        return False
    except Exception as e:
        print(f"Error sending FCM message: {e}")
        return False


def notify_opponent_matched(booking, opponent_user):
    """
    Send notification to opponent about the match.
    
    Args:
        booking: Booking object
        opponent_user: User object (the opponent)
    """
    court_name = booking.court.name if hasattr(booking.court, 'name') else 'Court'
    start_time = booking.start_time.strftime('%d %B, %H:%M')
    seeker_nickname = booking.user.nickname
    
    title_i18n = {
        'en': 'Match Found!',
        'ru': 'Матч найден!',
        'tk': 'Duşuşyk tapyldy!',
    }
    
    message_i18n = {
        'en': f'You have a match with {seeker_nickname} on {start_time} at {court_name}',
        'ru': f'У вас матч с {seeker_nickname} {start_time} на {court_name}',
        'tk': f'{seeker_nickname} bilen {start_time} wagtynda {court_name}-da duşuşygyňyz bar',
    }
    
    data = {
        'booking_id': str(booking.id),
        'opponent_id': str(booking.user.id),
        'opponent_nickname': seeker_nickname,
        'court_id': str(booking.court.id),
        'court_name': court_name,
        'start_time': booking.start_time.isoformat(),
        'end_time': booking.end_time.isoformat(),
    }
    
    return create_notification(
        user=opponent_user,
        notification_type='opponent_matched',
        title_i18n=title_i18n,
        message_i18n=message_i18n,
        data=data
    )


def notify_seeker_matched(booking, opponent_user):
    """
    Send notification to seeker about finding an opponent.
    
    Args:
        booking: Booking object
        opponent_user: User object (the opponent that was found)
    """
    court_name = booking.court.name if hasattr(booking.court, 'name') else 'Court'
    start_time = booking.start_time.strftime('%d %B, %H:%M')
    opponent_nickname = opponent_user.nickname
    
    title_i18n = {
        'en': 'Opponent Found!',
        'ru': 'Соперник найден!',
        'tk': 'Garşydaş tapyldy!',
    }
    
    message_i18n = {
        'en': f'Found opponent: {opponent_nickname}. Match on {start_time} at {court_name}',
        'ru': f'Найден соперник: {opponent_nickname}. Матч {start_time} на {court_name}',
        'tk': f'Garşydaş tapyldy: {opponent_nickname}. {start_time} wagtynda {court_name}-da duşuşyk',
    }
    
    data = {
        'booking_id': str(booking.id),
        'opponent_id': str(opponent_user.id),
        'opponent_nickname': opponent_nickname,
        'court_id': str(booking.court.id),
        'court_name': court_name,
        'start_time': booking.start_time.isoformat(),
        'end_time': booking.end_time.isoformat(),
    }
    
    return create_notification(
        user=booking.user,
        notification_type='opponent_matched',
        title_i18n=title_i18n,
        message_i18n=message_i18n,
        data=data
    )


def notify_booking_confirmed(booking):
    """Send notification about booking confirmation"""
    court_name = booking.court.name if hasattr(booking.court, 'name') else 'Court'
    start_time = booking.start_time.strftime('%d %B, %H:%M')
    
    title_i18n = {
        'en': 'Booking Confirmed',
        'ru': 'Бронирование подтверждено',
        'tk': 'Bronlaş tassyklandy',
    }
    
    message_i18n = {
        'en': f'Your booking at {court_name} on {start_time} is confirmed',
        'ru': f'Ваше бронирование на {court_name} {start_time} подтверждено',
        'tk': f'{court_name}-da {start_time} wagtyndaky bronlaşyňyz tassyklandy',
    }
    
    data = {
        'booking_id': str(booking.id),
        'court_id': str(booking.court.id),
        'court_name': court_name,
        'start_time': booking.start_time.isoformat(),
        'end_time': booking.end_time.isoformat(),
    }
    
    return create_notification(
        user=booking.user,
        notification_type='booking_confirmed',
        title_i18n=title_i18n,
        message_i18n=message_i18n,
        data=data
    )


def register_push_token(user, token, platform):
    """
    Register or update a push notification token for a user.
    
    Args:
        user: User object
        token: Push token string
        platform: Platform ('ios', 'android', 'web')
    
    Returns:
        PushToken object
    """
    # Check if token already exists
    existing_token = PushToken.objects(token=token).first()
    
    if existing_token:
        # Update existing token
        existing_token.user = user
        existing_token.platform = platform
        existing_token.is_active = True
        existing_token.last_used_at = datetime.utcnow()
        existing_token.save()
        return existing_token
    
    # Create new token
    push_token = PushToken(
        user=user,
        token=token,
        platform=platform,
        last_used_at=datetime.utcnow()
    )
    push_token.save()
    
    return push_token


def unregister_push_token(token):
    """
    Unregister a push notification token.
    
    Args:
        token: Push token string
    """
    push_token = PushToken.objects(token=token).first()
    if push_token:
        push_token.is_active = False
        push_token.save()

