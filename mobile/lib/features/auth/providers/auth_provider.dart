import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/user_model.dart';
import '../data/repositories/auth_repository.dart';
import '../../../core/services/firebase_messaging_service.dart';
import '../../../core/services/api_service.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository();
});

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(authRepositoryProvider), ref.read(apiServiceProvider));
});

class AuthState {
  final UserModel? user;
  final bool isLoading;
  final String? error;
  final bool isAuthenticated;
  
  AuthState({
    this.user,
    this.isLoading = false,
    this.error,
    bool? isAuthenticated,
  }) : isAuthenticated = isAuthenticated ?? user != null;
  
  AuthState copyWith({
    UserModel? user,
    bool? isLoading,
    String? error,
    bool? isAuthenticated,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      isAuthenticated: isAuthenticated ?? (user != null),
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _repository;
  final ApiService _apiService;
  
  AuthNotifier(this._repository, this._apiService) : super(AuthState()) {
    _loadUser();
  }
  
  Future<void> _loadUser() async {
    state = state.copyWith(isLoading: true);
    try {
      final user = await _repository.getCurrentUser();
      state = state.copyWith(user: user, isLoading: false);
      
      // Register FCM token if user is logged in
      if (user != null) {
        await FirebaseMessagingService.registerToken(_apiService);
      }
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }
  
  Future<bool> requestOTP(String phone) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _repository.requestOTP(phone);
      state = state.copyWith(isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
      return false;
    }
  }
  
  Future<bool> verifyOTP(String phone, String otp) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final user = await _repository.verifyOTP(phone, otp);
      state = state.copyWith(user: user, isLoading: false);
      
      // Register FCM token after successful login
      if (user != null) {
        await FirebaseMessagingService.registerToken(_apiService);
      }
      
      return true;
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
      return false;
    }
  }
  
  Future<void> logout() async {
    // Unregister FCM token before logout
    await FirebaseMessagingService.unregisterToken(_apiService);
    
    await _repository.logout();
    state = AuthState();
  }
}

