"""
Test script for push notifications
Usage: python manage.py shell < test_push_notification.py
"""

from datetime import datetime
from apps.users.models import User
from apps.notifications.services import create_notification

# Find a test user (replace with actual user)
try:
    # Get first user with a push token
    from apps.notifications.models import PushToken
    
    push_token = PushToken.objects(is_active=True).first()
    
    if not push_token:
        print("❌ No active push tokens found!")
        print("Please login to the mobile app first to register a token.")
        exit()
    
    user = push_token.user
    print(f"✅ Found user: {user.nickname} ({user.phone})")
    print(f"✅ Push token: {push_token.token[:50]}...")
    print(f"✅ Platform: {push_token.platform}")
    
    # Create a test notification
    print("\n📤 Sending test notification...")
    
    notification = create_notification(
        user=user,
        notification_type='system',
        title_i18n={
            'en': 'Test Notification',
            'ru': 'Тестовое уведомление',
            'tk': 'Synag habarnamasy',
        },
        message_i18n={
            'en': 'This is a test push notification from Sportlink!',
            'ru': 'Это тестовое push-уведомление от Sportlink!',
            'tk': 'Bu Sportlink-den synag push habarnamasy!',
        },
        data={
            'test': 'true',
            'timestamp': str(datetime.utcnow()),
        }
    )
    
    print(f"✅ Notification created: {notification.id}")
    print(f"✅ Sent: {notification.is_sent}")
    
    if notification.is_sent:
        print("\n🎉 Push notification sent successfully!")
        print("Check your mobile device for the notification.")
    else:
        print("\n⚠️ Notification created but not sent.")
        print("Check Firebase credentials and backend logs.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

