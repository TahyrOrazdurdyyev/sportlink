# Sportlink - Руководство по запуску проекта

## Обзор проекта

Sportlink - единая экосистема для спортсменов и организаций:
- Мобильное приложение (Flutter)
- Админ-панель (React)
- Backend API (Django)

## Предварительные требования

- Docker и Docker Compose
- Python 3.11+
- Node.js 18+
- Flutter 3.0+
- PostgreSQL 15+ с PostGIS
- Redis

## Быстрый старт

### 1. Backend (Django)

```bash
cd backend

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактировать .env файл

# Применить миграции
python manage.py makemigrations
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver
```

### 2. База данных и Redis (Docker)

```bash
# Запустить PostgreSQL и Redis
docker-compose up -d db redis

# Или все сервисы вместе
docker-compose up
```

### 3. Mobile App (Flutter)

```bash
cd mobile

# Установить зависимости
flutter pub get

# Настроить Firebase
# Добавить google-services.json (Android) и GoogleService-Info.plist (iOS)

# Запустить приложение
flutter run
```

### 4. Admin Panel (React)

```bash
cd admin

# Установить зависимости
npm install

# Запустить dev сервер
npm run dev
```

## Конфигурация

### Backend Environment Variables

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://sportlink:sportlink@localhost:5432/sportlink
REDIS_URL=redis://localhost:6379/0
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id
```

### Firebase Setup

1. Создать проект в Firebase Console
2. Включить Phone Authentication
3. Включить Cloud Messaging
4. Скачать credentials для Admin SDK
5. Настроить в backend .env файле

## Структура проекта

```
Sportlink/
├── backend/          # Django API
│   ├── apps/        # Django приложения
│   ├── sportlink/   # Настройки проекта
│   └── manage.py
├── mobile/          # Flutter приложение
│   ├── lib/
│   └── pubspec.yaml
├── admin/           # React админ-панель
│   ├── src/
│   └── package.json
└── docker-compose.yml
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/otp/request/` - Запрос OTP
- `POST /api/v1/auth/otp/verify/` - Проверка OTP

### Users
- `GET /api/v1/users/me/` - Текущий пользователь
- `PATCH /api/v1/users/me/` - Обновить профиль
- `GET /api/v1/users/{id}/` - Публичный профиль

### Search
- `GET /api/v1/search/partners/` - Поиск партнёров

### Courts
- `GET /api/v1/courts/` - Список кортов
- `GET /api/v1/courts/{id}/` - Детали корта

### Bookings
- `POST /api/v1/bookings/` - Создать бронирование
- `GET /api/v1/bookings/` - Список бронирований
- `PATCH /api/v1/bookings/{id}/cancel/` - Отменить бронирование

### Tournaments
- `GET /api/v1/tournaments/` - Список турниров
- `POST /api/v1/tournaments/{id}/register/` - Регистрация на турнир

### Admin
- `POST /api/v1/admin/categories/` - Создать категорию
- `POST /api/v1/admin/courts/` - Создать корт
- `POST /api/v1/admin/tariffs/` - Создать тариф
- `POST /api/v1/admin/tournaments/` - Создать турнир

## Миграции базы данных

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

## Тестирование

### Backend
```bash
cd backend
pytest
```

### Mobile
```bash
cd mobile
flutter test
```

## Production Deployment

1. Настроить переменные окружения
2. Использовать PostgreSQL с PostGIS
3. Настроить Redis для Celery
4. Настроить AWS S3 для медиа
5. Настроить SSL/HTTPS
6. Настроить мониторинг (Sentry, Prometheus)

## Поддержка

Для вопросов и проблем создавайте Issues в репозитории.

