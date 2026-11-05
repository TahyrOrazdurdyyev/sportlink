import 'dart:io';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../network/api_client.dart';

class FirebaseMessagingService {
  static final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  static String? _fcmToken;

  static Future<void> initialize() async {
    // Request permission for iOS
    if (Platform.isIOS) {
      NotificationSettings settings = await _firebaseMessaging.requestPermission(
        alert: true,
        announcement: false,
        badge: true,
        carPlay: false,
        criticalAlert: false,
        provisional: false,
        sound: true,
      );

      if (kDebugMode) {
        print('User granted permission: ${settings.authorizationStatus}');
      }
    }

    // Get FCM token
    _fcmToken = await _firebaseMessaging.getToken();
    if (kDebugMode) {
      print('FCM Token: $_fcmToken');
    }

    // Save token locally
    if (_fcmToken != null) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('fcm_token', _fcmToken!);
    }

    // Handle token refresh
    _firebaseMessaging.onTokenRefresh.listen((newToken) {
      if (kDebugMode) {
        print('FCM Token refreshed: $newToken');
      }
      _fcmToken = newToken;
      _registerTokenWithBackend(newToken);
    });

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // Handle background messages
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

    // Handle notification tap when app is in background
    FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);

    // Check if app was opened from a notification
    RemoteMessage? initialMessage = await _firebaseMessaging.getInitialMessage();
    if (initialMessage != null) {
      _handleNotificationTap(initialMessage);
    }
  }

  static Future<String?> getToken() async {
    if (_fcmToken != null) {
      return _fcmToken;
    }

    _fcmToken = await _firebaseMessaging.getToken();
    return _fcmToken;
  }

  static Future<void> registerToken(ApiClient apiService) async {
    final token = await getToken();
    if (token == null) {
      if (kDebugMode) {
        print('No FCM token available');
      }
      return;
    }

    try {
      final platform = Platform.isIOS ? 'ios' : 'android';
      await apiService.post('/push-tokens/register/', data: {
        'token': token,
        'platform': platform,
      });

      if (kDebugMode) {
        print('FCM token registered with backend');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error registering FCM token: $e');
      }
    }
  }

  static Future<void> unregisterToken(ApiClient apiService) async {
    final token = await getToken();
    if (token == null) return;

    try {
      await apiService.post('/push-tokens/unregister/', data: {
        'token': token,
      });

      if (kDebugMode) {
        print('FCM token unregistered from backend');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error unregistering FCM token: $e');
      }
    }
  }

  static Future<void> _registerTokenWithBackend(String token) async {
    // Get token from shared preferences to check if user is logged in
    final prefs = await SharedPreferences.getInstance();
    final authToken = prefs.getString('auth_token');
    
    if (authToken == null) {
      if (kDebugMode) {
        print('User not logged in, skipping token registration');
      }
      return;
    }

    try {
      final platform = Platform.isIOS ? 'ios' : 'android';
      // Create API service instance with auth token
      // Note: This is a simplified version, you might need to adjust based on your ApiClient implementation
      final apiService = ApiClient();
      await apiService.post('/push-tokens/register/', data: {
        'token': token,
        'platform': platform,
      });

      if (kDebugMode) {
        print('FCM token registered with backend');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error registering FCM token: $e');
      }
    }
  }

  static void _handleForegroundMessage(RemoteMessage message) {
    if (kDebugMode) {
      print('Received foreground message: ${message.messageId}');
      print('Title: ${message.notification?.title}');
      print('Body: ${message.notification?.body}');
      print('Data: ${message.data}');
    }

    // You can show a local notification here or update UI
    // For now, we'll just log it
  }

  static void _handleNotificationTap(RemoteMessage message) {
    if (kDebugMode) {
      print('Notification tapped: ${message.messageId}');
      print('Data: ${message.data}');
    }

    // Handle navigation based on notification data
    final data = message.data;
    
    if (data.containsKey('booking_id')) {
      // Navigate to booking details
      // You'll need to implement navigation logic here
      if (kDebugMode) {
        print('Navigate to booking: ${data['booking_id']}');
      }
    } else if (data.containsKey('match_id')) {
      // Navigate to match details
      if (kDebugMode) {
        print('Navigate to match: ${data['match_id']}');
      }
    }
  }

  static Future<void> deleteToken() async {
    await _firebaseMessaging.deleteToken();
    _fcmToken = null;
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('fcm_token');
    
    if (kDebugMode) {
      print('FCM token deleted');
    }
  }
}

// Top-level function for background message handling
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  if (kDebugMode) {
    print('Handling background message: ${message.messageId}');
    print('Title: ${message.notification?.title}');
    print('Body: ${message.notification?.body}');
    print('Data: ${message.data}');
  }
}

