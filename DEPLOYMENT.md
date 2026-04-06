# Инструкция по развертыванию на сервере

## Развертывание через Docker

### Требования
- Docker и Docker Compose установлены на сервере
- Домен `sportlink.com.tm` настроен на IP `216.250.13.53`

### 1. Подготовка на сервере

```bash
# Клонируйте репозиторий или загрузите файлы проекта
cd /path/to/sportlink

# Создайте файл .env из примера
cp .env.example .env

# Отредактируйте .env файл:
nano .env
```

### 2. Настройка .env файла

```env
# Django Settings
DEBUG=False
SECRET_KEY=ваш-секретный-ключ-для-продакшена

# Server Configuration (поддерживает и домен, и IP)
BASE_URL=https://sportlink.com.tm
# Или: BASE_URL=http://216.250.13.53:8000

# Allowed Hosts
ALLOWED_HOSTS=sportlink.com.tm,www.sportlink.com.tm,216.250.13.53

# CORS
CORS_ALLOWED_ORIGINS=https://sportlink.com.tm,http://sportlink.com.tm,http://216.250.13.53

# MongoDB (в Docker используйте имя сервиса)
MONGODB_NAME=sportlink
MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_USERNAME=
MONGODB_PASSWORD=

# Redis
REDIS_URL=redis://redis:6379/0
```

### 3. Запуск через Docker Compose

```bash
# Соберите и запустите все сервисы
docker-compose up -d --build

# Проверьте статус
docker-compose ps

# Просмотр логов
docker-compose logs -f backend
```

### 4. Миграция данных из локальной разработки

```bash
# На локальной машине: создайте бэкап MongoDB
mongodump --db sportlink --out ./backup

# Скопируйте бэкап на сервер
scp -r ./backup user@216.250.13.53:/tmp/

# На сервере: восстановите данные
docker exec -i sportlink_mongodb mongorestore --db sportlink /tmp/backup/sportlink
```

### 5. Обновление кода без Git

```bash
# Вариант 1: Экспорт Docker образа
# На локальной машине:
docker build -t sportlink-backend:latest ./backend
docker save sportlink-backend:latest | gzip > backend-image.tar.gz
scp backend-image.tar.gz user@216.250.13.53:/tmp/

# На сервере:
gunzip -c /tmp/backend-image.tar.gz | docker load
docker-compose up -d --no-deps backend

# Вариант 2: Копирование файлов
# Скопируйте измененные файлы на сервер
scp -r backend/ user@216.250.13.53:/path/to/sportlink/
# Перезапустите контейнер
docker-compose restart backend
```

## Развертывание без Docker (альтернатива)

### 1. Backend (Django)

```bash
# Установите переменные окружения на сервере
export BASE_URL=https://sportlink.com.tm
export SECRET_KEY=ваш-секретный-ключ
export DEBUG=False
export ALLOWED_HOSTS=sportlink.com.tm,www.sportlink.com.tm,216.250.13.53

# Запустите backend через gunicorn
cd backend
gunicorn sportlink.wsgi:application --bind 0.0.0.0:8000
```

### 2. Mobile App (Flutter)

```bash
# Соберите APK для продакшена (поддерживает и домен, и IP)
cd mobile
flutter build apk --release --dart-define=API_BASE_URL=https://sportlink.com.tm
# Или: flutter build apk --release --dart-define=API_BASE_URL=http://216.250.13.53:8000

# APK файл будет в: build/app/outputs/flutter-apk/app-release.apk
```

### 3. Admin Panel (React)

```bash
# Обновите API URL в .env файле (поддерживает и домен, и IP)
echo "VITE_API_BASE_URL=https://sportlink.com.tm/api/v1" > admin/.env
# Или: echo "VITE_API_BASE_URL=http://216.250.13.53:8000/api/v1" > admin/.env

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
    listen [::]:80;
    server_name sportlink.com.tm www.sportlink.com.tm;

    # Редирект на HTTPS (рекомендуется)
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name sportlink.com.tm www.sportlink.com.tm;

    # SSL сертификаты (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/sportlink.com.tm/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sportlink.com.tm/privkey.pem;

    # Для Docker
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Медиа файлы из Docker volume
    location /media/ {
        alias /path/to/sportlink/backend/media/;
    }

    # Статические файлы из Docker volume
    location /static/ {
        alias /path/to/sportlink/backend/staticfiles/;
    }
}
```

## Проверка работоспособности

После развертывания:

1. ✅ Откройте `https://sportlink.com.tm/api/v1/categories/` - должен вернуть JSON
2. ✅ Откройте `http://216.250.13.53:8000/api/v1/categories/` - должен вернуть JSON (работает и по IP)
3. ✅ Установите APK на телефон и проверьте загрузку категорий
4. ✅ Откройте админ-панель и войдите
5. ✅ Проверьте отображение изображений в приложении

### Проверка Docker контейнеров

```bash
# Статус всех сервисов
docker-compose ps

# Логи backend
docker-compose logs backend

# Логи MongoDB
docker-compose logs mongodb

# Проверка подключения к MongoDB
docker exec -it sportlink_mongodb mongosh sportlink
```

## Полезные команды

```bash
# Проверить текущий IP (для локальной разработки)
ipconfig getifaddr en0  # macOS
ip addr show           # Linux

# Проверить работу backend (работает и по домену, и по IP)
curl https://sportlink.com.tm/api/v1/categories/
curl http://216.250.13.53:8000/api/v1/categories/

# Docker команды
docker-compose ps                    # Статус сервисов
docker-compose logs -f backend       # Логи в реальном времени
docker-compose restart backend       # Перезапуск backend
docker-compose down                  # Остановка всех сервисов
docker-compose up -d --build         # Пересборка и запуск

# MongoDB команды
docker exec -it sportlink_mongodb mongosh sportlink  # Подключение к БД
docker exec sportlink_mongodb mongodump --db sportlink --out /tmp/backup  # Бэкап
```

