import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  // Для локальной разработки: используйте IP вашего компьютера
  // Для продакшена: используйте доменное имя
  static const String _localDevUrl = 'http://192.168.1.97:8000/api/v1';
  static const String _productionUrl = 'https://api.sportlink.tm/api/v1'; // Замените на ваш домен
  
  // Автоматически использовать production URL если задан, иначе local
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: _localDevUrl, // Для локальной разработки
  );
  
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
    return apiBaseUrl.replaceAll('/api/v1', '');
  }
}
