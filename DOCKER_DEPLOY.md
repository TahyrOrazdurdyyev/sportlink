# Быстрый старт с Docker

## Настройка для продакшена

### 1. Создайте файл `.env` в корне проекта:

```env
DEBUG=False
SECRET_KEY=ваш-секретный-ключ-для-продакшена
BASE_URL=https://sportlink.com.tm
ALLOWED_HOSTS=sportlink.com.tm,www.sportlink.com.tm,216.250.13.53
CORS_ALLOWED_ORIGINS=https://sportlink.com.tm,http://sportlink.com.tm,http://216.250.13.53
MONGODB_NAME=sportlink
MONGODB_HOST=mongodb
MONGODB_PORT=27017
REDIS_URL=redis://redis:6379/0
```

### 2. Запуск:

```bash
docker-compose up -d --build
```

### 3. Проверка:

```bash
# Статус сервисов
docker-compose ps

# Логи
docker-compose logs -f backend

# Проверка API
curl https://sportlink.com.tm/api/v1/categories/
curl http://216.250.13.53:8000/api/v1/categories/
```

## Миграция данных

### Экспорт с локальной машины:

```bash
mongodump --db sportlink --out ./backup
```

### Импорт на сервер:

```bash
# Скопируйте папку backup на сервер, затем:
docker exec -i sportlink_mongodb mongorestore --db sportlink /path/to/backup/sportlink
```

## Обновление кода без Git

### Вариант 1: Копирование файлов

```bash
# Скопируйте измененные файлы
scp -r backend/ user@216.250.13.53:/path/to/sportlink/

# Перезапустите контейнер
ssh user@216.250.13.53 "cd /path/to/sportlink && docker-compose restart backend"
```

### Вариант 2: Docker образ

```bash
# На локальной машине:
docker build -t sportlink-backend:latest ./backend
docker save sportlink-backend:latest | gzip > backend-image.tar.gz
scp backend-image.tar.gz user@216.250.13.53:/tmp/

# На сервере:
gunzip -c /tmp/backend-image.tar.gz | docker load
cd /path/to/sportlink
docker-compose up -d --no-deps backend
```

## Важные моменты

- ✅ Приложение работает **и по домену**, **и по IP**
- ✅ Все настройки через переменные окружения в `.env`
- ✅ MongoDB, Redis и Backend в отдельных контейнерах
- ✅ Данные сохраняются в Docker volumes

## Остановка и очистка

```bash
# Остановка
docker-compose down

# Остановка с удалением volumes (⚠️ удалит данные!)
docker-compose down -v
```
