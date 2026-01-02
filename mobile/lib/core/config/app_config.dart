import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  // Backend URL будет определяться автоматически из переменной окружения
  // Для локальной разработки: flutter run --dart-define=API_BASE_URL=http://192.168.1.64:8000
  // Для продакшена: flutter build apk --dart-define=API_BASE_URL=https://api.sportlink.tm
  
  static const String _defaultUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://192.168.1.64:8000', // Fallback для разработки
  );
  
  static String get baseUrl => _defaultUrl;
  static String get apiBaseUrl => '$_defaultUrl/api/v1';
  
  static SharedPreferences? _prefs;
  
  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }
  
  static SharedPreferences get prefs {
    if (_prefs == null) {
      throw Exception('AppConfig not initialized. Call AppConfig.init() first.');
    }
    return _prefs!;
  }
  
  // Вспомогательный метод для получения базового URL медиа-файлов
  static String get mediaBaseUrl {
    return baseUrl;
  }
  
  // Метод для очистки кэша (для решения проблемы с login loop)
  static Future<void> clearCache() async {
    await _prefs?.remove('user_data');
    await _prefs?.remove('access_token');
    await _prefs?.remove('refresh_token');
  }
}
