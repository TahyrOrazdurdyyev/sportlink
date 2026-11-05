import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/user_model.dart';
import '../data/repositories/auth_repository.dart';
import '../../../core/network/api_client.dart';
import '../../../core/services/firebase_messaging_service.dart';

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(authRepositoryProvider), ref.read(apiClientProvider));
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
  final ApiClient _apiClient;
  
  AuthNotifier(this._repository, this._apiClient) : super(AuthState()) {
    _loadUser();
  }
  
  Future<void> _loadUser() async {
    state = state.copyWith(isLoading: true);
    try {
      final user = await _repository.getCurrentUser();
      state = state.copyWith(user: user, isLoading: false);
      
      // Register FCM token if user is logged in
      if (user != null) {
        await FirebaseMessagingService.registerToken(_apiClient);
      }
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }
  
  Future<bool> login({required String login, required String password}) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _repository.login(login: login, password: password);
      final user = await _repository.getCurrentUser();
      state = state.copyWith(user: user, isAuthenticated: true, isLoading: false);
      await FirebaseMessagingService.registerToken(_apiClient);
      return true;
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
      return false;
    }
  }
  
  Future<void> logout() async {
    // Unregister FCM token before logout
    await FirebaseMessagingService.unregisterToken(_apiClient);
    
    await _repository.logout();
    state = AuthState();
  }
}

