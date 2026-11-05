# Sportlink - Configuration Guide

## Локальная разработка

### Backend (Django)

1. IP адрес меняется? Не проблема! Django настроен принимать запросы с любых IP (`ALLOWED_HOSTS = *`)

2. Для изменения BASE_URL (если нужно):
```bash
export BASE_URL=http://YOUR_LOCAL_IP:8000
python manage.py runserver 0.0.0.0:8000
```

### Mobile (Flutter)

1. Измените IP в файле `mobile/lib/core/config/app_config.dart`:
```dart
static const String _localDevUrl = 'http://YOUR_LOCAL_IP:8000/api/v1';
```

2. Или используйте переменную окружения при сборке:
```bash
flutter run --dart-define=API_BASE_URL=http://YOUR_IP:8000/api/v1
```

## Продакшен (Production)

### Backend

1. Установите переменные окружения:
```bash
export DEBUG=False
export ALLOWED_HOSTS=api.sportlink.tm,sportlink.tm
export BASE_URL=https://api.sportlink.tm
export SECRET_KEY=your-super-secret-key
```

2. Используйте `.env` файл или настройки сервера для переменных окружения

### Mobile

Соберите приложение с production URL:
```bash
flutter build apk --dart-define=API_BASE_URL=https://api.sportlink.tm/api/v1
```

## Быстрое обновление IP для разработки

Если ваш локальный IP изменился, просто обновите одну строку в:
- `mobile/lib/core/config/app_config.dart` - строка `_localDevUrl`
- Backend автоматически примет новый IP (ALLOWED_HOSTS = *)

## Автоматическое обновление URL изображений

После изменения IP запустите:
```bash
cd backend
python fix_image_urls.py  # Обновит URLs в базе данных
```

