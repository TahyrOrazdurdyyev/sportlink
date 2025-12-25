import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:firebase_core/firebase_core.dart';

import 'firebase_options.dart';
import 'core/config/app_config.dart';
import 'core/theme/app_theme.dart';
import 'core/l10n/app_localizations.dart';
import 'core/providers/locale_provider.dart';
import 'core/services/firebase_messaging_service.dart';
import 'features/auth/presentation/screens/auth_screen.dart';
import 'features/auth/data/repositories/auth_repository.dart';
import 'features/home/home_screen.dart';
import 'features/profile/profile_screen.dart';
import 'features/profile/edit_profile_screen.dart';
import 'features/bookings/booking_history_screen.dart';
import 'features/subscription/subscription_plans_screen.dart';
import 'features/settings/settings_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  
  // Initialize app config
  await AppConfig.init();
  
  // Initialize Firebase Messaging
  await FirebaseMessagingService.initialize();
  
  runApp(
    const ProviderScope(
      child: SportlinkApp(),
    ),
  );
}

class SportlinkApp extends ConsumerWidget {
  const SportlinkApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final locale = ref.watch(localeProvider);
    
    return MaterialApp(
      title: 'Sportlink',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      
      // Localization support
      locale: locale,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en'),
        Locale('ru'),
        Locale('tk'),
      ],
      
      // Routes
      routes: {
        '/auth': (context) => const AuthScreen(),
        '/home': (context) => const HomeScreen(),
        '/profile': (context) => const ProfileScreen(),
        '/edit-profile': (context) => const EditProfileScreen(),
        '/booking-history': (context) => const BookingHistoryScreen(),
        '/subscription': (context) => const SubscriptionPlansScreen(),
        '/settings': (context) => const SettingsScreen(),
      },
      
      // Start with Home screen (no auth required for browsing)
      home: const HomeScreen(),
    );
  }
}
