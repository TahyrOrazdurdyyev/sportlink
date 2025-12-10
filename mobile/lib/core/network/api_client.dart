import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  ApiClient._internal();
  
  late Dio _dio;
  
  void init() {
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
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            // Token expired, try refresh
            final refreshed = await _refreshToken();
            if (refreshed) {
              // Retry request
              final opts = error.requestOptions;
              final prefs = AppConfig.prefs;
              final token = prefs.getString('access_token');
              if (token != null) {
                opts.headers['Authorization'] = 'Bearer $token';
                final response = await _dio.fetch(opts);
                return handler.resolve(response);
              }
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
      if (refreshToken == null) return false;
      
      final response = await _dio.post(
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
  
  Dio get dio => _dio;
}

