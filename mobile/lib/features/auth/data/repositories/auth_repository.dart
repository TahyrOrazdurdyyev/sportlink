import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/config/app_config.dart';
import '../models/user_model.dart';
import 'dart:convert';

class AuthRepository {
  final ApiClient _apiClient = ApiClient();
  
  /// Register a new user
  Future<bool> register({
    required String firstName,
    required String lastName,
    required String nickname,
    required String phone,
    required String password,
  }) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/register/',
        data: {
          'first_name': firstName,
          'last_name': lastName,
          'nickname': nickname,
          'phone': phone,
          'password': password,
          'password_confirm': password, // Backend expects password_confirm
        },
      );
      
      // Store tokens
      final prefs = AppConfig.prefs;
      await prefs.setString('access_token', response.data['access']);
      await prefs.setString('refresh_token', response.data['refresh']);
      
      // Store user data
      await prefs.setString('user_data', jsonEncode(response.data['user']));
      
      return true;
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Registration failed');
      }
      throw Exception('Registration failed: ${e.message}');
    } catch (e) {
      throw Exception('Registration failed: $e');
    }
  }
  
  /// Login user (using phone or nickname)
  Future<bool> login({
    required String login, // Can be phone or nickname
    required String password,
  }) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/login/',
        data: {
          'identifier': login, // Backend expects 'identifier'
          'password': password,
        },
      );
      
      // Store tokens
      final prefs = AppConfig.prefs;
      await prefs.setString('access_token', response.data['access']);
      await prefs.setString('refresh_token', response.data['refresh']);
      
      // Store user data
      print('DEBUG LOGIN: Response data: ${response.data}');
      print('DEBUG LOGIN: User data: ${response.data['user']}');
      await prefs.setString('user_data', jsonEncode(response.data['user']));
      final stored = prefs.getString('user_data');
      print('DEBUG LOGIN: Stored user_data: $stored');
      
      return true;
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Login failed');
      }
      throw Exception('Login failed: ${e.message}');
    } catch (e) {
      throw Exception('Login failed: $e');
    }
  }
  
  /// Logout user
  Future<void> logout() async {
    // Clear local storage
    final prefs = AppConfig.prefs;
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    await prefs.remove('user_data');
  }
  
  /// Get current user from cache or API
  Future<UserModel?> getCurrentUser() async {
    try {
      final prefs = AppConfig.prefs;
      
      // Try to get from cache first
      final userData = prefs.getString('user_data');
      print('DEBUG getCurrentUser: userData from cache: $userData');
      
      if (userData != null) {
        final userJson = jsonDecode(userData) as Map<String, dynamic>;
        print('DEBUG getCurrentUser: Parsed user JSON: $userJson');
        final user = UserModel.fromJson(userJson);
        print('DEBUG getCurrentUser: Created UserModel: ${user.firstName} ${user.lastName}');
        return user;
      }
      
      print('DEBUG getCurrentUser: No cached data, fetching from API');
      // Fetch from API if not in cache
      final response = await _apiClient.dio.get('/users/me/');
      final user = UserModel.fromJson(response.data);
      
      // Cache user
      await prefs.setString('user_data', jsonEncode(user.toJson()));
      
      return user;
    } catch (e) {
      print('DEBUG getCurrentUser: ERROR: $e');
      return null;
    }
  }
  
  /// Check if user is authenticated
  Future<bool> isAuthenticated() async {
    final prefs = AppConfig.prefs;
    final accessToken = prefs.getString('access_token');
    return accessToken != null && accessToken.isNotEmpty;
  }
}

// Riverpod provider
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository();
});
