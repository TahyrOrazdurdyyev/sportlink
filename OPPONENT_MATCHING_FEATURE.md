# Opponent Matching & Notification System

## Overview
Implemented automatic opponent matching system with real-time notifications for court bookings.

## Features
- Automatic opponent matching when creating bookings
- Real-time notifications for both seeker and opponent
- Display matched opponent information (nickname, full name)
- Match history tracking
- Push notification support (infrastructure ready)

## Backend Implementation

### 1. Models

#### OpponentMatch (`backend/apps/bookings/matching.py`)
Tracks opponent matches between users:
- `booking` - Reference to the booking
- `seeker` - User looking for opponent
- `opponent` - Matched opponent
- `status` - Match status (pending, accepted, declined, matched, cancelled)
- `opponents_needed` - Number of opponents needed
- `opponents_found` - Number of opponents found
- Notification tracking flags

#### OpponentRequest (`backend/apps/bookings/matching.py`)
Tracks users actively looking for opponents:
- `user` - User looking for opponent
- `booking` - Associated booking
- `skill_level` - Preferred skill level
- `is_active` - Whether request is active
- `expires_at` - When request expires (1 hour before match)

#### Notification (`backend/apps/notifications/models.py`)
Stores user notifications:
- `user` - Recipient
- `type` - Notification type (opponent_matched, booking_confirmed, etc.)
- `title` - i18n title (EN, RU, TK)
- `message` - i18n message (EN, RU, TK)
- `data` - Additional data (booking_id, opponent_id, etc.)
- `is_read` - Read status
- `is_sent` - Push notification sent status

#### PushToken (`backend/apps/notifications/models.py`)
Stores user's push notification tokens:
- `user` - User reference
- `token` - FCM/APNS token
- `platform` - Platform (ios, android, web)
- `is_active` - Active status

### 2. Matching Logic (`backend/apps/bookings/matching.py`)

**`find_opponent_for_booking(booking)`**
- Finds potential opponents for a booking
- Searches for bookings at same time/court looking for opponents
- Filters out bookings that already have enough opponents

**`create_opponent_match(booking, opponent_booking)`**
- Creates a match between two bookings
- Adds opponents to each other's participants list
- Returns OpponentMatch object

**`auto_match_opponents(booking)`**
- Automatically matches opponents when booking is created
- Matches up to `opponents_needed` opponents
- Returns list of created matches

### 3. Notification Services (`backend/apps/notifications/services.py`)

**`create_notification(user, type, title_i18n, message_i18n, data)`**
- Creates a notification for a user
- Supports i18n (EN, RU, TK)
- Triggers push notification sending

**`notify_opponent_matched(booking, opponent_user)`**
- Sends notification to opponent about the match
- Includes: opponent nickname, date, time, court name
- Data: booking_id, opponent_id, court details

**`notify_seeker_matched(booking, opponent_user)`**
- Sends notification to seeker about finding opponent
- Includes: opponent nickname, date, time, court name
- Data: booking_id, opponent_id, court details

**`register_push_token(user, token, platform)`**
- Registers/updates push notification token
- Supports iOS, Android, Web

**`send_push_notification(notification)`**
- Sends push notification to user's devices
- Infrastructure ready for Firebase/OneSignal integration
- Automatically uses user's preferred language

### 4. API Endpoints

#### Bookings
- `POST /api/v1/bookings/` - Create booking (auto-matches opponents)
  - Returns `matches_found` and `matched_opponents` if matches found

#### Opponent Matching
- `GET /api/v1/bookings/<booking_id>/matches/` - Get matches for a booking
- `GET /api/v1/bookings/matches/my/` - Get all user's matches
- `GET /api/v1/bookings/matches/find/?booking_id=<id>` - Find potential opponents

#### Notifications
- `GET /api/v1/notifications/` - List user's notifications
- `POST /api/v1/notifications/<id>/mark_read/` - Mark notification as read
- `POST /api/v1/notifications/mark_all_read/` - Mark all as read
- `GET /api/v1/notifications/unread_count/` - Get unread count

#### Push Tokens
- `POST /api/v1/push-tokens/register/` - Register push token
- `POST /api/v1/push-tokens/unregister/` - Unregister push token

## Mobile App Implementation

### 1. Models (`mobile/lib/core/models/notification.dart`)

**Notification**
- Stores notification data
- `getTitle(locale)` - Get localized title
- `getMessage(locale)` - Get localized message

**OpponentMatch**
- Stores match information
- `role` - 'seeker' or 'opponent'
- `opponent` - Opponent info
- `booking` - Match booking info

**OpponentInfo**
- Opponent details (id, nickname, name)
- `fullName` getter

**MatchBookingInfo**
- Booking details for match
- Court, time, status

### 2. Screens

#### NotificationsScreen (`mobile/lib/features/notifications/notifications_screen.dart`)
- Displays all user notifications
- Shows unread count in app bar
- Mark as read on tap
- Mark all as read button
- Refresh functionality
- Time ago display
- Icon based on notification type
- Navigation to relevant screens

#### MyMatchesScreen (`mobile/lib/features/bookings/presentation/screens/my_matches_screen.dart`)
- Displays all user's matches
- Shows role (seeker/opponent)
- Opponent information with avatar
- Match details (court, date, time)
- Status badges
- Time ago for match creation
- Refresh functionality

#### CreateBookingScreen (Updated)
- Shows dialog when opponents are matched
- Displays matched opponent(s) information
- Success message about notifications sent

### 3. User Flow

1. **User A creates booking with "find opponents"**
   - Selects court, date, time
   - Enables "Find Opponents"
   - Specifies number of opponents needed
   - Submits booking

2. **System auto-matches**
   - Searches for User B with matching booking
   - Creates OpponentMatch
   - Adds users to each other's participants

3. **Notifications sent**
   - User A: "Opponent Found! @userB"
   - User B: "Match Found! @userA on [date] at [time] at [court]"

4. **User A sees dialog**
   - "Opponent(s) Found!"
   - Shows matched opponent(s) with nickname and name
   - Info: "Both you and your opponent(s) have been notified"

5. **Both users receive notifications**
   - In-app notification
   - Push notification (if enabled)
   - Can view in Notifications screen

6. **Users can view matches**
   - Navigate to "My Matches"
   - See all past and upcoming matches
   - View opponent details
   - See match status

## Notification Examples

### Opponent Matched (to Opponent)
```json
{
  "type": "opponent_matched",
  "title": {
    "en": "Match Found!",
    "ru": "Матч найден!",
    "tk": "Duşuşyk tapyldy!"
  },
  "message": {
    "en": "You have a match with @john on 25 December, 10:00 at Tennis Court #1",
    "ru": "У вас матч с @john 25 декабря, 10:00 на Теннисный корт #1",
    "tk": "@john bilen 25-nji dekabr, 10:00 wagtynda Tennis Court #1-da duşuşygyňyz bar"
  },
  "data": {
    "booking_id": "...",
    "opponent_id": "...",
    "opponent_nickname": "john",
    "court_id": "...",
    "court_name": "Tennis Court #1",
    "start_time": "2025-12-25T10:00:00Z",
    "end_time": "2025-12-25T12:00:00Z"
  }
}
```

### Opponent Found (to Seeker)
```json
{
  "type": "opponent_matched",
  "title": {
    "en": "Opponent Found!",
    "ru": "Соперник найден!",
    "tk": "Garşydaş tapyldy!"
  },
  "message": {
    "en": "Found opponent: @mike. Match on 25 December, 10:00 at Tennis Court #1",
    "ru": "Найден соперник: @mike. Матч 25 декабря, 10:00 на Теннисный корт #1",
    "tk": "Garşydaş tapyldy: @mike. 25-nji dekabr, 10:00 wagtynda Tennis Court #1-da duşuşyk"
  },
  "data": {
    "booking_id": "...",
    "opponent_id": "...",
    "opponent_nickname": "mike",
    "court_id": "...",
    "court_name": "Tennis Court #1",
    "start_time": "2025-12-25T10:00:00Z",
    "end_time": "2025-12-25T12:00:00Z"
  }
}
```

## API Response Examples

### Create Booking with Matched Opponents
```http
POST /api/v1/bookings/
{
  "court": "court-uuid",
  "start_time": "2025-12-25T10:00:00Z",
  "end_time": "2025-12-25T12:00:00Z",
  "find_opponents": true,
  "opponents_needed": 1
}
```

**Response (201):**
```json
{
  "id": "booking-uuid",
  "court": "court-uuid",
  "start_time": "2025-12-25T10:00:00Z",
  "end_time": "2025-12-25T12:00:00Z",
  "find_opponents": true,
  "opponents_needed": 1,
  "status": "pending",
  "matches_found": 1,
  "matched_opponents": [
    {
      "id": "user-uuid",
      "nickname": "mike",
      "first_name": "Mike",
      "last_name": "Johnson"
    }
  ]
}
```

### Get My Matches
```http
GET /api/v1/bookings/matches/my/
```

**Response (200):**
```json
{
  "matches_count": 2,
  "matches": [
    {
      "match_id": "match-uuid-1",
      "role": "seeker",
      "opponent": {
        "id": "user-uuid",
        "nickname": "mike",
        "first_name": "Mike",
        "last_name": "Johnson"
      },
      "booking": {
        "id": "booking-uuid",
        "court_id": "court-uuid",
        "court_name": "Tennis Court #1",
        "start_time": "2025-12-25T10:00:00Z",
        "end_time": "2025-12-25T12:00:00Z",
        "status": "confirmed"
      },
      "matched_at": "2025-12-24T15:30:00Z"
    },
    {
      "match_id": "match-uuid-2",
      "role": "opponent",
      "opponent": {
        "id": "user-uuid-2",
        "nickname": "sarah",
        "first_name": "Sarah",
        "last_name": "Smith"
      },
      "booking": {
        "id": "booking-uuid-2",
        "court_id": "court-uuid-2",
        "court_name": "Basketball Court",
        "start_time": "2025-12-26T14:00:00Z",
        "end_time": "2025-12-26T16:00:00Z",
        "status": "pending"
      },
      "matched_at": "2025-12-24T16:00:00Z"
    }
  ]
}
```

## Push Notification Integration

### Setup (To be implemented)

1. **Firebase Cloud Messaging (FCM)**
   ```python
   # backend/apps/notifications/services.py
   import firebase_admin
   from firebase_admin import messaging
   
   def send_to_fcm(token, title, body, data):
       message = messaging.Message(
           notification=messaging.Notification(
               title=title,
               body=body,
           ),
           data=data,
           token=token,
       )
       response = messaging.send(message)
       return response
   ```

2. **Mobile App (Flutter)**
   ```dart
   // Register token
   final token = await FirebaseMessaging.instance.getToken();
   await apiService.post('/push-tokens/register/', data: {
     'token': token,
     'platform': 'android', // or 'ios'
   });
   
   // Handle notifications
   FirebaseMessaging.onMessage.listen((RemoteMessage message) {
     // Show local notification
   });
   ```

## Testing Checklist

### Backend
- [x] Create booking with find_opponents=true
- [x] Auto-match opponents when both users book same slot
- [x] Create notifications for both seeker and opponent
- [x] API endpoints return correct data
- [x] Notification i18n works for all languages
- [ ] Push notification sending (requires FCM setup)

### Mobile App
- [x] Display matched opponents dialog after booking
- [x] Show notifications in NotificationsScreen
- [x] Display matches in MyMatchesScreen
- [x] Mark notifications as read
- [x] Navigate from notification to booking
- [ ] Receive push notifications (requires FCM setup)
- [ ] Register/unregister push tokens

## Future Enhancements
- Opponent acceptance/decline flow
- Skill level matching
- Location-based matching
- Match reminders (1 hour before, 1 day before)
- Chat between matched opponents
- Match rating and feedback
- Match history statistics
- Favorite opponents
- Block/report users
- Group matches (4+ players)

