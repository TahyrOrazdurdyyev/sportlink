# Firebase Push Notifications Setup

## ✅ Completed Setup

### Flutter (Mobile App)
- ✅ Firebase Core initialized
- ✅ Firebase Messaging configured
- ✅ FCM Service created (`lib/core/services/fcm_service.dart`)
- ✅ Token handling in AuthRepository
- ✅ Background message handler
- ✅ Foreground message handler

### Android
- ✅ `google-services.json` configured
- ✅ Firebase dependencies added to `build.gradle.kts`
- ✅ Package name: `tm.sportlink.app`

### iOS
- ✅ `GoogleService-Info.plist` configured
- ✅ Firebase initialized in `AppDelegate.swift`
- ✅ Bundle ID: `tm.sportlink.app`
- ⚠️ **APNs NOT configured** (requires Apple Developer Account $99/год)

### Django Backend
- ✅ Firebase Admin SDK initialized
- ✅ FCM token field in User model
- ✅ Endpoint for updating FCM tokens (`/api/v1/users/fcm-token/`)
- ✅ Push notification utilities (`apps/notifications/fcm_utils.py`)
- ✅ Celery tasks for notifications (`apps/notifications/tasks.py`)

---

## 🚀 Usage

### 1. Enable Phone Authentication in Firebase Console
1. Go to Firebase Console → Authentication → Sign-in method
2. Enable **Phone** authentication
3. Save

### 2. Test Push Notifications (Android Only)

#### From Django Shell:
```python
python manage.py shell

from apps.users.models import User
from apps.notifications.fcm_utils import send_push_notification

# Get a user with FCM token
user = User.objects.filter(fcm_token__exists=True).first()

# Send test notification
send_push_notification(
    token=user.fcm_token,
    title='Test Notification',
    body='This is a test push notification!',
    data={'type': 'test'}
)
```

#### Using Celery Tasks:
```python
from apps.notifications.tasks import send_custom_notification

# Send async notification
send_custom_notification.delay(
    user_id=str(user.id),
    title='Async Test',
    body='This notification was sent via Celery',
    data={'type': 'async_test'}
)
```

### 3. Common Notification Scenarios

#### Booking Confirmation:
```python
from apps.notifications.tasks import send_booking_confirmation_notification

send_booking_confirmation_notification.delay(
    user_id=str(user.id),
    booking_id=str(booking.id),
    court_name='Central Tennis Court',
    time='14:00 - 15:00',
)
```

#### Tournament Reminder:
```python
from apps.notifications.tasks import send_tournament_reminder_notification

send_tournament_reminder_notification.delay(
    tournament_id=str(tournament.id),
    hours_before=24,
)
```

#### Broadcast to All Users:
```python
from apps.notifications.tasks import send_broadcast_notification

send_broadcast_notification.delay(
    title='Important Announcement',
    body='Platform maintenance scheduled for tonight',
    data={'type': 'announcement'},
)
```

---

## 📱 Flutter Integration

### Get FCM Token:
```dart
import 'package:your_app/core/services/fcm_service.dart';

final fcmService = FCMService();
await fcmService.initialize();
final token = fcmService.fcmToken;
print('FCM Token: $token');
```

### Subscribe to Topics:
```dart
await fcmService.subscribeToTopic('all_users');
await fcmService.subscribeToTopic('tournament_updates');
```

### Handle Notification Click:
Edit `lib/core/services/fcm_service.dart` in the `_handleMessage` method to add navigation logic.

---

## 🔧 iOS Setup (When Ready)

1. **Get Apple Developer Account** ($99/year)
2. **Create APNs Authentication Key:**
   - Go to [Apple Developer Console](https://developer.apple.com/account/resources/authkeys/list)
   - Create new key with APNs enabled
   - Download `.p8` file
   - Note **Key ID** and **Team ID**

3. **Upload to Firebase:**
   - Firebase Console → Project Settings → Cloud Messaging
   - Scroll to **Apple app configuration**
   - Click **Upload** under APNs Authentication Key
   - Upload `.p8` file and enter Key ID & Team ID

---

## 🧪 Testing

### Test FCM Token Registration:
```bash
# Start backend
cd backend
python3.11 manage.py runserver

# In another terminal, test endpoint
curl -X POST http://localhost:8000/api/v1/users/fcm-token/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fcm_token": "test_token_123"}'
```

### Test from Firebase Console:
1. Firebase Console → Cloud Messaging → **Send test message**
2. Enter **FCM Token** (get from app logs)
3. Enter title & body
4. Send

---

## 📊 Monitoring

### Check FCM Logs:
```bash
# Django logs
tail -f logs/django.log | grep FCM

# Celery logs
tail -f logs/celery.log | grep notification
```

### Firebase Console:
- Go to **Cloud Messaging** → **Reports**
- View delivery success/failure rates

---

## ⚠️ Important Notes

1. **Android**: Push notifications work immediately
2. **iOS**: Requires APNs configuration (Apple Developer Account)
3. **Token Expiry**: FCM tokens can expire/refresh - handled automatically
4. **Batch Limit**: Max 500 tokens per multicast message
5. **Rate Limits**: Firebase has rate limits on messages sent

---

## 🐛 Troubleshooting

### No FCM Token:
- Check app permissions (notifications allowed)
- Check Firebase initialization in logs
- Verify `google-services.json` is in correct location

### Notifications Not Received:
- Check FCM token is saved in backend
- Verify Firebase Admin SDK is initialized
- Check Firebase Console for delivery errors
- Ensure app is in foreground/background (not force-closed)

### iOS Not Working:
- APNs key must be configured
- Check Bundle ID matches Firebase settings
- Verify `GoogleService-Info.plist` is in correct location

---

## 📚 Resources

- [Firebase Cloud Messaging Docs](https://firebase.google.com/docs/cloud-messaging)
- [Flutter Firebase Messaging Plugin](https://pub.dev/packages/firebase_messaging)
- [Firebase Admin Python SDK](https://firebase.google.com/docs/admin/setup)

