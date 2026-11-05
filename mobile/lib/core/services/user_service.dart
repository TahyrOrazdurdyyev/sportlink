import 'package:dio/dio.dart';
import 'package:sportlink/core/network/api_client.dart';
import 'package:sportlink/features/auth/data/models/user_model.dart';
import 'package:sportlink/core/config/app_config.dart';
import 'dart:convert';
import 'dart:io';

class UserService {
  final ApiClient _apiClient = ApiClient();

  /// Update user profile
  Future<UserModel> updateProfile(Map<String, dynamic> data) async {
    try {
      final response = await _apiClient.patch(
        '/users/me/update/',
        data: data,
      );
      
      // Update cached user data
      final updatedUser = UserModel.fromJson(response.data);
      final prefs = AppConfig.prefs;
      await prefs.setString('user_data', jsonEncode(response.data));
      
      return updatedUser;
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Failed to update profile');
      }
      throw Exception('Failed to update profile: ${e.message}');
    } catch (e) {
      throw Exception('Failed to update profile: $e');
    }
  }

  /// Get current user profile
  Future<UserModel> getCurrentUser() async {
    try {
      final response = await _apiClient.dio.get('/users/me/');
      return UserModel.fromJson(response.data);
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Failed to get user profile');
      }
      throw Exception('Failed to get user profile: ${e.message}');
    } catch (e) {
      throw Exception('Failed to get user profile: $e');
    }
  }

  /// Upload avatar image
  Future<String> uploadAvatar(File imageFile) async {
    try {
      // Create multipart form data
      final formData = FormData.fromMap({
        'avatar': await MultipartFile.fromFile(
          imageFile.path,
          filename: imageFile.path.split('/').last,
        ),
      });

      final response = await _apiClient.dio.post(
        '/users/avatar/upload/',
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      return response.data['avatar_url'] as String;
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Failed to upload avatar');
      }
      throw Exception('Failed to upload avatar: ${e.message}');
    } catch (e) {
      throw Exception('Failed to upload avatar: $e');
    }
  }

  /// Delete avatar image
  Future<void> deleteAvatar() async {
    try {
      await _apiClient.dio.delete('/users/avatar/delete/');
    } on DioException catch (e) {
      if (e.response?.data != null && e.response?.data is Map) {
        final errorData = e.response?.data as Map;
        throw Exception(errorData['error'] ?? 'Failed to delete avatar');
      }
      throw Exception('Failed to delete avatar: ${e.message}');
    } catch (e) {
      throw Exception('Failed to delete avatar: $e');
    }
  }
}

