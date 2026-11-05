# Firebase Cloud Messaging Setup Guide

## Overview
This guide explains how to complete the Firebase Cloud Messaging (FCM) setup for push notifications.

## Current Status ✅

### Mobile App (Flutter)
- ✅ Firebase dependencies added (`firebase_core`, `firebase_messaging`)
- ✅ Configuration files present:
  - `android/app/google-services.json`
  - `ios/Runner/GoogleService-Info.plist`
- ✅ Firebase initialized in `main.dart`
- ✅ `FirebaseMessagingService` created with:
  - Token management
  - Foreground/background message handling
  - Notification tap handling
  - Auto-registration on login
  - Auto-unregistration on logout

### Backend (Django)
- ✅ Push notification infrastructure ready
- ✅ `PushToken` model for storing device tokens
- ✅ API endpoints for token registration
- ✅ Notification system with i18n support
- ✅ FCM integration code implemented

## What's Left to Do

### 1. Backend: Install Firebase Admin SDK

```bash
cd backend
pip install firebase-admin
pip freeze > requirements.txt
```

### 2. Backend: Get Firebase Service Account Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click on **Project Settings** (gear icon)
4. Go to **Service Accounts** tab
5. Click **Generate New Private Key**
6. Download the JSON file
7. Save it as `firebase-credentials.json` in your backend root directory

**⚠️ IMPORTANT:** Add to `.gitignore`:
```
firebase-credentials.json
```

### 3. Backend: Set Environment Variable (Optional)

If you want to store the credentials file elsewhere:

```bash
export FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-credentials.json
```

Or add to your `.env` file:
```
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-credentials.json
```

### 4. Mobile: Verify Firebase Configuration

#### Android

Check `android/app/build.gradle`:
```gradle
dependencies {
    // ... other dependencies
    implementation platform('com.google.firebase:firebase-bom:32.7.0')
    implementation 'com.google.firebase:firebase-messaging'
}
```

Check `android/build.gradle`:
```gradle
buildscript {
    dependencies {
        // ... other dependencies
        classpath 'com.google.gms:google-services:4.4.0'
    }
}
```

At the bottom of `android/app/build.gradle`:
```gradle
apply plugin: 'com.google.gms.google-services'
```

#### iOS

1. Open `ios/Runner.xcworkspace` in Xcode
2. Verify `GoogleService-Info.plist` is in the project
3. Enable Push Notifications capability:
   - Select Runner target
   - Go to "Signing & Capabilities"
   - Click "+ Capability"
   - Add "Push Notifications"
   - Add "Background Modes" and check "Remote notifications"

### 5. Test Push Notifications

#### Backend Test Script

Create `backend/test_push.py`:
```python
from apps.notifications.services import send_to_fcm

# Test with a device token
token = "YOUR_DEVICE_TOKEN_HERE"
title = "Test Notification"
body = "This is a test push notification"
data = {"test": "true"}

success = send_to_fcm(token, title, body, data)
print(f"Notification sent: {success}")
```

Run:
```bash
python manage.py shell < test_push.py
```

#### Get Device Token

In your Flutter app, the FCM token is printed to console on startup:
```
FCM Token: fXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Or you can add a button in the app to display it:
```dart
final token = await FirebaseMessagingService.getToken();
print('My FCM Token: $token');
```

## How It Works

### Flow Diagram

```
┌─────────────┐
│   User      │
│   Logs In   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  Get FCM Token          │
│  (FirebaseMessaging)    │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Register Token         │
│  POST /push-tokens/     │
│  register/              │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Store in Database      │
│  (PushToken model)      │
└─────────────────────────┘

       ... later ...

┌─────────────────────────┐
│  Event Occurs           │
│  (Opponent Matched)     │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Create Notification    │
│  (Notification model)   │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Get User's Tokens      │
│  (PushToken.objects)    │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Send via FCM           │
│  (Firebase Admin SDK)   │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  User Receives          │
│  Push Notification      │
└─────────────────────────┘
```

## Code Overview

### Mobile App

**Initialization (`main.dart`):**
```dart
await Firebase.initializeApp();
await FirebaseMessagingService.initialize();
```

**Token Registration (`auth_provider.dart`):**
```dart
// After successful login
await FirebaseMessagingService.registerToken(_apiService);

// Before logout
await FirebaseMessagingService.unregisterToken(_apiService);
```

**Message Handling (`firebase_messaging_service.dart`):**
```dart
// Foreground messages
FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

// Background messages
FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

// Notification tap
FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);
```

### Backend

**Token Storage (`notifications/models.py`):**
```python
class PushToken(Document):
    user = fields.ReferenceField(User)
    token = fields.StringField(required=True, unique=True)
    platform = fields.StringField(choices=['ios', 'android', 'web'])
    is_active = fields.BooleanField(default=True)
```

**Sending Notifications (`notifications/services.py`):**
```python
def notify_opponent_matched(booking, opponent_user):
    title_i18n = {
        'en': 'Match Found!',
        'ru': 'Матч найден!',
        'tk': 'Duşuşyk tapyldy!',
    }
    
    message_i18n = {
        'en': f'You have a match with {seeker_nickname}...',
        'ru': f'У вас матч с {seeker_nickname}...',
        'tk': f'{seeker_nickname} bilen duşuşygyňyz bar...',
    }
    
    return create_notification(
        user=opponent_user,
        notification_type='opponent_matched',
        title_i18n=title_i18n,
        message_i18n=message_i18n,
        data=data
    )
```

**FCM Integration (`notifications/services.py`):**
```python
def send_to_fcm(token, title, body, data):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data_payload,
        token=token,
    )
    
    response = messaging.send(message)
    return True
```

## Notification Types

Currently implemented:
- `opponent_matched` - When an opponent is found for a match
- `booking_confirmed` - When a booking is confirmed
- `booking_cancelled` - When a booking is cancelled
- `match_reminder` - Reminder before a match (future)
- `payment_received` - Payment confirmation (future)
- `tournament_update` - Tournament updates (future)
- `system` - System notifications (future)

## Troubleshooting

### Token Not Registering

1. Check if Firebase is initialized:
   ```dart
   await Firebase.initializeApp();
   ```

2. Check if user is logged in:
   ```dart
   final authToken = prefs.getString('auth_token');
   ```

3. Check backend logs for errors

### Notifications Not Received

1. **Check token is registered:**
   ```bash
   # In Django shell
   from apps.notifications.models import PushToken
   PushToken.objects(user=your_user)
   ```

2. **Check notification was created:**
   ```bash
   from apps.notifications.models import Notification
   Notification.objects(user=your_user).order_by('-created_at').first()
   ```

3. **Check Firebase credentials:**
   ```bash
   ls -la firebase-credentials.json
   ```

4. **Test with Firebase Console:**
   - Go to Firebase Console > Cloud Messaging
   - Send a test notification to your device token

### iOS Notifications Not Working

1. Verify Push Notifications capability is enabled
2. Check provisioning profile includes push notifications
3. Test on a real device (push doesn't work on simulator)
4. Check iOS notification permissions:
   ```dart
   NotificationSettings settings = await _firebaseMessaging.requestPermission();
   print('Permission status: ${settings.authorizationStatus}');
   ```

### Android Notifications Not Working

1. Check `google-services.json` is in `android/app/`
2. Verify Google Services plugin is applied
3. Check notification channel is created (Android 8+)
4. Test with `adb logcat` to see errors

## Security Best Practices

1. **Never commit Firebase credentials:**
   ```gitignore
   firebase-credentials.json
   google-services.json
   GoogleService-Info.plist
   ```

2. **Use environment variables in production:**
   ```python
   import os
   cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH')
   ```

3. **Validate tokens on backend:**
   - Check token format
   - Deactivate invalid tokens
   - Rate limit registration requests

4. **Secure API endpoints:**
   - Require authentication
   - Validate user owns the token
   - Prevent token enumeration

## Production Deployment

### Backend

1. Install Firebase Admin SDK:
   ```bash
   pip install firebase-admin
   ```

2. Set environment variable:
   ```bash
   export FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json
   ```

3. Update `requirements.txt`:
   ```bash
   pip freeze > requirements.txt
   ```

### Mobile App

1. Build release APK/IPA with Firebase configuration
2. Test push notifications on production build
3. Monitor Firebase Console for delivery metrics

## Monitoring

### Firebase Console

- **Cloud Messaging** tab shows:
  - Sent notifications
  - Delivery rate
  - Open rate
  - Errors

### Backend Logs

Monitor for:
- Token registration/unregistration
- Notification creation
- FCM send success/failure
- Invalid token deactivation

### Database Queries

```python
# Count active tokens
PushToken.objects(is_active=True).count()

# Count notifications sent today
from datetime import datetime, timedelta
today = datetime.utcnow().replace(hour=0, minute=0, second=0)
Notification.objects(created_at__gte=today, is_sent=True).count()

# Find users with no tokens
from apps.users.models import User
users_without_tokens = []
for user in User.objects():
    if not PushToken.objects(user=user, is_active=True):
        users_without_tokens.append(user)
```

## Next Steps

1. ✅ Install `firebase-admin` on backend
2. ✅ Download and configure Firebase credentials
3. ✅ Test push notifications
4. ✅ Deploy to production
5. Monitor delivery metrics
6. Implement additional notification types
7. Add notification preferences (user settings)
8. Implement notification scheduling
9. Add rich notifications (images, actions)
10. Implement notification analytics

