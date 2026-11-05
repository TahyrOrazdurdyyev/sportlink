import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/app_config.dart';

// Provider for ApiClient
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  ApiClient._internal() {
    _initDio();
  }
  
  late Dio _dio;
  
  void _initDio() {
    _dio = Dio(BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));
    
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add auth token
          final prefs = AppConfig.prefs;
          final token = prefs.getString('access_token');
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          // Don't try to refresh if already refreshing or if it's the refresh endpoint
          if (error.response?.statusCode == 401 && 
              !error.requestOptions.path.contains('/auth/token/refresh/')) {
            // Token expired, try refresh ONCE
            final refreshed = await _refreshToken();
            if (refreshed) {
              // Retry request
              final opts = error.requestOptions;
              final prefs = AppConfig.prefs;
              final token = prefs.getString('access_token');
              if (token != null && token.isNotEmpty) {
                opts.headers['Authorization'] = 'Bearer $token';
                try {
                  final response = await _dio.fetch(opts);
                  return handler.resolve(response);
                } catch (e) {
                  // If retry fails, clear tokens and pass error
                  await _clearTokens();
                  return handler.next(error);
                }
              }
            } else {
              // Refresh failed, clear tokens
              await _clearTokens();
            }
          }
          return handler.next(error);
        },
      ),
    );
  }
  
  Future<bool> _refreshToken() async {
    try {
      final prefs = AppConfig.prefs;
      final refreshToken = prefs.getString('refresh_token');
      if (refreshToken == null || refreshToken.isEmpty) return false;
      
      // Use a new Dio instance to avoid interceptor loop
      final tempDio = Dio(BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ));
      
      final response = await tempDio.post(
        '/auth/token/refresh/',
        data: {'refresh': refreshToken},
      );
      
      final newAccessToken = response.data['access'];
      await prefs.setString('access_token', newAccessToken);
      return true;
    } catch (e) {
      return false;
    }
  }
  
  Future<void> _clearTokens() async {
    final prefs = AppConfig.prefs;
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
    await prefs.remove('user_data');
  }
  
  Dio get dio => _dio;
  
  // HTTP methods
  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) {
    return _dio.get(path, queryParameters: queryParameters);
  }
  
  Future<Response> post(String path, {dynamic data, Map<String, dynamic>? queryParameters}) {
    return _dio.post(path, data: data, queryParameters: queryParameters);
  }
  
  Future<Response> put(String path, {dynamic data, Map<String, dynamic>? queryParameters}) {
    return _dio.put(path, data: data, queryParameters: queryParameters);
  }
  
  Future<Response> delete(String path, {dynamic data, Map<String, dynamic>? queryParameters}) {
    return _dio.delete(path, data: data, queryParameters: queryParameters);
  }
  
  Future<Response> patch(String path, {dynamic data, Map<String, dynamic>? queryParameters}) {
    return _dio.patch(path, data: data, queryParameters: queryParameters);
  }
}

