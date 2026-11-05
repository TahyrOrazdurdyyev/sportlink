import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/otp_verification_screen.dart';
import '../../features/auth/presentation/screens/auth_screen.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/profile/presentation/screens/profile_screen.dart';
import '../../features/profile/edit_profile_screen.dart';
import '../../features/search/presentation/screens/search_partners_screen.dart';
import '../../features/courts/presentation/screens/courts_list_screen.dart';
import '../../features/courts/presentation/screens/court_detail_screen.dart';
import '../../features/bookings/presentation/screens/bookings_list_screen.dart';
import '../../features/bookings/booking_history_screen.dart';
import '../../features/tournaments/presentation/screens/tournaments_list_screen.dart';
import '../../features/tournaments/presentation/screens/tournament_detail_screen.dart';
import '../../features/subscription/subscription_plans_screen.dart';
import '../../features/settings/settings_screen.dart';
import '../../features/auth/providers/auth_provider.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/home',
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/otp-verify',
        builder: (context, state) {
          final phone = state.uri.queryParameters['phone'] ?? '';
          return OTPVerificationScreen(phone: phone);
        },
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/profile',
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/search/partners',
        builder: (context, state) => const SearchPartnersScreen(),
      ),
      GoRoute(
        path: '/courts',
        builder: (context, state) => const CourtsListScreen(),
      ),
      GoRoute(
        path: '/courts/:id',
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return CourtDetailScreen(courtId: id);
        },
      ),
      GoRoute(
        path: '/bookings',
        builder: (context, state) => const BookingsListScreen(),
      ),
      GoRoute(
        path: '/tournaments',
        builder: (context, state) => const TournamentsListScreen(),
      ),
      GoRoute(
        path: '/tournaments/:id',
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return TournamentDetailScreen(tournamentId: id);
        },
      ),
      GoRoute(
        path: '/auth',
        builder: (context, state) => const AuthScreen(),
      ),
      GoRoute(
        path: '/edit-profile',
        builder: (context, state) => const EditProfileScreen(),
      ),
      GoRoute(
        path: '/booking-history',
        builder: (context, state) => const BookingHistoryScreen(),
      ),
      GoRoute(
        path: '/subscription',
        builder: (context, state) => const SubscriptionPlansScreen(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
    ],
  );
});

