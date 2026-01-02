# Инструкция по развертыванию на сервере

## Подготовка сервера

### 1. Backend (Django)

```bash
# Установите переменные окружения на сервере
export BASE_URL=https://api.sportlink.tm
export DJANGO_SECRET_KEY=ваш-секретный-ключ
export DJANGO_DEBUG=False

# Запустите backend через gunicorn или uwsgi
cd backend
gunicorn sportlink.wsgi:application --bind 0.0.0.0:8000
```

### 2. Mobile App (Flutter)

```bash
# Соберите APK для продакшена
cd mobile
flutter build apk --release --dart-define=API_BASE_URL=https://api.sportlink.tm

# APK файл будет в: build/app/outputs/flutter-apk/app-release.apk
```

### 3. Admin Panel (React)

```bash
# Обновите API URL в .env файле
echo "VITE_API_BASE_URL=https://api.sportlink.tm/api/v1" > admin/.env

# Соберите для продакшена
cd admin
npm run build

# Файлы для деплоя будут в папке dist/
```

## Важные моменты

### Без изменения кода!

Все настройки теперь через переменные окружения:

- **Backend:** `BASE_URL` environment variable
- **Mobile:** `--dart-define=API_BASE_URL` при сборке
- **Admin:** `.env` файл или переменная окружения

### Миграция данных

При первом развертывании выполните:

```bash
cd backend
python manage.py migrate
python migrate_opponent_search_field.py  # Для существующих пользователей
```

### Настройка NGINX (пример)

```nginx
server {
    listen 80;
    server_name api.sportlink.tm;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /media/ {
        alias /path/to/backend/media/;
    }

    location /static/ {
        alias /path/to/backend/static/;
    }
}
```

## Проверка работоспособности

После развертывания:

1. ✅ Откройте `https://api.sportlink.tm/api/v1/categories/` - должен вернуть JSON
2. ✅ Установите APK на телефон и проверьте загрузку категорий
3. ✅ Откройте админ-панель и войдите
4. ✅ Проверьте отображение изображений в приложении

## Полезные команды

```bash
# Проверить текущий IP (для локальной разработки)
ipconfig getifaddr en0  # macOS
ip addr show           # Linux

# Проверить работу backend
curl https://api.sportlink.tm/api/v1/categories/

# Просмотр логов
tail -f backend/logs/django.log
```

