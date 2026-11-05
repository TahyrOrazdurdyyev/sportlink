# Subscription Features - Полная реализация

## ✅ Реализованные функции

### 1. Проверка конфликтов бронирований ✅

**Файлы:**
- `backend/apps/bookings/views.py` - улучшенная проверка конфликтов
- `backend/apps/bookings/models.py` - валидация в модели

**API Endpoints:**
```
GET /api/v1/bookings/check-availability/
  ?court_id=UUID&start_time=ISO&end_time=ISO
  
POST /api/v1/bookings/  (с автоматической проверкой конфликтов)
```

**Функционал:**
- ✅ Проверка доступности площадки перед бронированием
- ✅ Обнаружение пересекающихся бронирований
- ✅ Возврат списка конфликтующих бронирований
- ✅ HTTP 409 Conflict при попытке забронировать занятое время
- ✅ Real-time проверка (статус pending/confirmed)

**Пример ответа:**
```json
{
  "available": false,
  "court_id": "uuid",
  "requested_start": "2024-01-15T14:00:00",
  "requested_end": "2024-01-15T16:00:00",
  "conflicts": [
    {
      "id": "uuid",
      "start_time": "2024-01-15T15:00:00",
      "end_time": "2024-01-15T17:00:00",
      "status": "confirmed"
    }
  ]
}
```

---

### 2. Подбор соперника по уровню ✅

**Файлы:**
- `backend/apps/users/views_matching.py` - алгоритм подбора

**API Endpoints:**
```
GET /api/v1/users/find-opponents/
  ?experience_level=5&city=Ashgabat&category_id=UUID&limit=20
  
POST /api/v1/users/match-invitation/
  Body: {opponent_id, court_id, proposed_time, message}
```

**Функционал:**
- ✅ Поиск по уровню опыта (±1 от уровня пользователя)
- ✅ Фильтрация по городу
- ✅ Фильтрация по спортивным категориям
- ✅ Расчет совместимости (0-100 баллов)
  - Схожесть уровня опыта (40 баллов)
  - Общие категории спорта (30 баллов)
  - Локация (20 баллов)
  - Схожесть рейтинга (10 баллов)
- ✅ Отправка приглашений на матч
- ✅ Push-уведомления при приглашении
- ✅ **Требует подписку с feature 'opponent_matching'**

**Пример ответа:**
```json
{
  "count": 15,
  "results": [
    {
      "id": "uuid",
      "first_name": "John",
      "last_name": "Doe",
      "experience_level": 5,
      "rating": 4.5,
      "city": "Ashgabat",
      "categories": [...],
      "compatibility_score": 85,
      "last_active": "2024-01-15T..."
    }
  ]
}
```

---

### 3. Расширенная статистика пользователя ✅

**Файлы:**
- `backend/apps/users/views_statistics.py` - комплексная аналитика

**API Endpoints:**
```
GET /api/v1/users/statistics/?range=30  (свои данные)
GET /api/v1/users/{user_id}/statistics/  (других пользователей)
GET /api/v1/users/achievements/
GET /api/v1/users/leaderboard/
```

**Функционал:**
- ✅ История бронирований (всего, подтверждено, отменено, завершено)
- ✅ Общее время игры (часы)
- ✅ Общие расходы
- ✅ Наиболее посещаемые площадки
- ✅ Участие в турнирах
- ✅ Активность по дням недели
- ✅ Активность по часам дня
- ✅ Метрики производительности:
  - Среднее количество бронирований в неделю
  - Процент завершенных бронирований
  - Процент отмененных бронирований
- ✅ Достижения и вехи
- ✅ Таблицы лидеров (по рейтингу, по бронированиям)
- ✅ **Требует подписку с feature 'advanced_statistics'**

**Пример ответа:**
```json
{
  "user": {...},
  "time_range": {"days": 30, "start_date": "..."},
  "bookings": {
    "total": 25,
    "confirmed": 20,
    "cancelled": 2,
    "completed": 18,
    "total_hours": 45.5,
    "total_spent": 2250.0
  },
  "tournaments": {
    "total_participated": 3,
    "list": [...]
  },
  "activity_patterns": {
    "by_day_of_week": {"Monday": 5, "Tuesday": 3, ...},
    "by_hour_of_day": {"14": 8, "18": 12, ...}
  },
  "performance": {
    "average_bookings_per_week": 5.8,
    "completion_rate": 72.0,
    "cancellation_rate": 8.0
  },
  "recent_activity": [...]
}
```

---

### 4. Система подписок и проверка доступа ✅

**Файлы:**
- `backend/apps/subscriptions/models_user.py` - модель UserSubscription
- `backend/apps/subscriptions/permissions.py` - декоратор @require_feature
- `backend/apps/subscriptions/views_user.py` - управление подписками

**API Endpoints:**
```
GET /api/v1/admin/subscriptions/my-subscription/  (текущая подписка)
POST /api/v1/admin/subscriptions/subscribe/  (оформить подписку)
POST /api/v1/admin/subscriptions/cancel/  (отменить подписку)
GET /api/v1/admin/subscriptions/my-features/  (доступные функции)
```

**Функционал:**
- ✅ Модель UserSubscription (активная подписка пользователя)
- ✅ Автоматическая проверка срока действия
- ✅ Декоратор `@require_feature(feature_key)` для защиты endpoints
- ✅ Автоматический HTTP 403 при отсутствии подписки или feature
- ✅ Поддержка месячных и годовых подписок
- ✅ Автопродление (флаг is_auto_renew)
- ✅ История транзакций

**Защищенные endpoints:**
- `GET /api/v1/users/find-opponents/` - требует `opponent_matching`
- `POST /api/v1/users/match-invitation/` - требует `opponent_matching`
- `GET /api/v1/users/statistics/` - требует `advanced_statistics`
- `GET /api/v1/users/achievements/` - требует `advanced_statistics`

**Оформление подписки:**
```json
POST /api/v1/admin/subscriptions/subscribe/
{
  "plan_id": "uuid",
  "period": "monthly",  // or "yearly"
  "payment_method": "card",
  "transaction_id": "TXN123"
}
```

**Ответ при отсутствии доступа:**
```json
HTTP 403 Forbidden
{
  "error": "Feature not available",
  "feature": "opponent_matching",
  "current_plan": {"en": "Sport+", ...},
  "message": "This feature is not included in your current plan"
}
```

---

## 📊 Доступные Features

| Feature Key | Название | Описание |
|------------|----------|----------|
| `court_booking` | Аренда площадки | Возможность бронирования спортивных площадок |
| `opponent_matching` | Подбор соперника | Поиск партнеров соответствующего уровня |
| `weekend_booking` | Бронирование в выходные | Возможность бронирования в субботу и воскресенье |
| `tournament_registration` | Регистрация на турниры | Участие в турнирах |
| `equipment_rental` | Аренда экипировки | Аренда ракеток, мячей и т.д. |
| `advanced_statistics` | Расширенная статистика | Подробная аналитика игр |
| `discount_court_booking` | Скидка на аренду | Скидки при бронировании площадок |

---

## 🔒 Как работает защита features

### 1. Декоратор @require_feature

```python
from apps.subscriptions.permissions import require_feature

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@require_feature('opponent_matching')
def find_opponents(request):
    # Этот код выполнится только если:
    # 1. Пользователь авторизован
    # 2. У пользователя есть активная подписка
    # 3. В подписке включен feature 'opponent_matching'
    ...
```

### 2. Программная проверка

```python
from apps.subscriptions.permissions import check_user_feature_access

has_access, message = check_user_feature_access(user, 'opponent_matching')
if not has_access:
    return Response({'error': message}, status=403)
```

### 3. Получение всех features пользователя

```python
from apps.subscriptions.permissions import get_user_features

features = get_user_features(user)
# {'court_booking': True, 'opponent_matching': False, ...}
```

---

## 🚀 Использование

### Проверка доступности площадки:

```bash
curl "http://localhost:8000/api/v1/bookings/check-availability/?court_id=UUID&start_time=2024-01-15T14:00:00Z&end_time=2024-01-15T16:00:00Z" \
  -H "Authorization: Bearer TOKEN"
```

### Поиск соперников:

```bash
curl "http://localhost:8000/api/v1/users/find-opponents/?experience_level=5&city=Ashgabat&limit=10" \
  -H "Authorization: Bearer TOKEN"
```

### Получение статистики:

```bash
curl "http://localhost:8000/api/v1/users/statistics/?range=30" \
  -H "Authorization: Bearer TOKEN"
```

### Оформление подписки:

```bash
curl -X POST http://localhost:8000/api/v1/admin/subscriptions/subscribe/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "uuid-of-prosport-plan",
    "period": "monthly",
    "payment_method": "card"
  }'
```

---

## 📁 Созданные файлы

### Backend:
- `apps/bookings/views.py` - проверка конфликтов
- `apps/users/views_matching.py` - подбор соперников
- `apps/users/views_statistics.py` - статистика и достижения
- `apps/subscriptions/models_user.py` - модель UserSubscription
- `apps/subscriptions/permissions.py` - декоратор @require_feature
- `apps/subscriptions/views_user.py` - управление подписками

---

## 🎯 Готово!

**Все features реализованы и защищены системой подписок!** 🎉

- ✅ Проверка конфликтов бронирований
- ✅ Подбор соперника по уровню с алгоритмом совместимости
- ✅ Расширенная статистика с достижениями и лидербордами
- ✅ Система подписок с автоматической проверкой доступа
- ✅ Защита endpoints через декораторы
- ✅ API для управления подписками

**Готово к использованию!** Перезапустите backend для применения изменений.

