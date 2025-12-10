import 'package:firebase_auth/firebase_auth.dart';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/config/app_config.dart';
import '../models/user_model.dart';

class AuthRepository {
  final ApiClient _apiClient = ApiClient();
  final FirebaseAuth _firebaseAuth = FirebaseAuth.instance;
  
  Future<bool> requestOTP(String phone) async {
    try {
      // Firebase handles OTP sending
      await _firebaseAuth.verifyPhoneNumber(
        phoneNumber: phone,
        verificationCompleted: (PhoneAuthCredential credential) {},
        verificationFailed: (FirebaseAuthException e) {
          throw Exception(e.message);
        },
        codeSent: (String verificationId, int? resendToken) {
          // Store verification ID
          AppConfig.prefs.setString('verification_id', verificationId);
        },
        codeAutoRetrievalTimeout: (String verificationId) {},
      );
      
      // Notify backend
      await _apiClient.dio.post(
        '/auth/otp/request/',
        data: {'phone': phone},
      );
      
      return true;
    } catch (e) {
      throw Exception('Failed to send OTP: $e');
    }
  }
  
  Future<UserModel> verifyOTP(String phone, String otp) async {
    try {
      final prefs = AppConfig.prefs;
      final verificationId = prefs.getString('verification_id');
      
      if (verificationId == null) {
        throw Exception('Verification ID not found');
      }
      
      // Create credential
      final credential = PhoneAuthProvider.credential(
        verificationId: verificationId,
        smsCode: otp,
      );
      
      // Sign in with Firebase
      final userCredential = await _firebaseAuth.signInWithCredential(credential);
      final firebaseToken = await userCredential.user?.getIdToken();
      
      if (firebaseToken == null) {
        throw Exception('Failed to get Firebase token');
      }
      
      // Verify with backend
      final response = await _apiClient.dio.post(
        '/auth/otp/verify/',
        data: {
          'phone': phone,
          'firebaseIdToken': firebaseToken,
        },
      );
      
      // Store tokens
      await prefs.setString('access_token', response.data['access']);
      await prefs.setString('refresh_token', response.data['refresh']);
      
      // Parse user
      return UserModel.fromJson(response.data['user']);
    } catch (e) {
      throw Exception('Failed to verify OTP: $e');
    }
  }
  
  Future<void> logout() async {
    await _firebaseAuth.signOut();
    final prefs = AppConfig.prefs;
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    await prefs.remove('user_data');
  }
  
  Future<UserModel?> getCurrentUser() async {
    try {
      final prefs = AppConfig.prefs;
      final userData = prefs.getString('user_data');
      if (userData != null) {
        // Return cached user
        // In real app, you'd parse JSON here
        return null;
      }
      
      // Fetch from API
      final response = await _apiClient.dio.get('/users/me/');
      final user = UserModel.fromJson(response.data);
      
      // Cache user
      // await prefs.setString('user_data', jsonEncode(user.toJson()));
      
      return user;
    } catch (e) {
      return null;
    }
  }
}

