# Инструкции по сборке приложения

## Для локальной разработки

### 1. Узнайте IP адрес вашего компьютера:

**macOS/Linux:**
```bash
ipconfig getifaddr en0
# или
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Windows:**
```cmd
ipconfig
```

### 2. Запустите backend:
```bash
cd backend
source venv/bin/activate  # macOS/Linux
# или venv\Scripts\activate  # Windows
python manage.py runserver 0.0.0.0:8000
```

### 3. Соберите и установите приложение:

**Debug версия (для разработки):**
```bash
cd mobile
flutter run --dart-define=API_BASE_URL=http://ВАШ_IP:8000
# Например: flutter run --dart-define=API_BASE_URL=http://192.168.1.64:8000
```

**Release версия (для тестирования):**
```bash
cd mobile
flutter build apk --release --dart-define=API_BASE_URL=http://ВАШ_IP:8000
flutter install --release
```

## Для продакшена (на сервере)

### 1. Соберите APK для продакшена:
```bash
cd mobile
flutter build apk --release --dart-define=API_BASE_URL=https://api.sportlink.tm
```

### 2. Соберите AAB для Google Play:
```bash
cd mobile
flutter build appbundle --release --dart-define=API_BASE_URL=https://api.sportlink.tm
```

### 3. Соберите для iOS (требуется macOS):
```bash
cd mobile
flutter build ios --release --dart-define=API_BASE_URL=https://api.sportlink.tm
```

## Примечания

- **API_BASE_URL** должен быть БЕЗ `/api/v1` в конце
- Для локальной разработки используйте IP адрес компьютера (не localhost!)
- Телефон и компьютер должны быть в одной Wi-Fi сети
- Если IP изменился, пересоберите приложение с новым IP

## Текущая конфигурация

- **Локальная разработка:** `http://192.168.1.64:8000`
- **Продакшн (планируется):** `https://api.sportlink.tm`

## Устранение проблем

### Проблема: Connection Error
**Решение:** 
1. Проверьте IP адрес компьютера
2. Убедитесь, что backend запущен
3. Пересоберите приложение с правильным IP

### Проблема: Login/Sign up по кругу
**Решение:** 
1. Удалите приложение с телефона
2. Установите новую версию
3. Кэш будет автоматически очищен при ошибках парсинга

### Проблема: Фотографии не отображаются
**Решение:** 
1. Убедитесь, что `API_BASE_URL` указан правильно
2. Проверьте, что backend отдает полные URL для медиа

