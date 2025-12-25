import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://192.168.31.106:8000/api/v1',
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
}

