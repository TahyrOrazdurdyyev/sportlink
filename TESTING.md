# Тестирование новых features

## ✅ Все features реализованы!

### Что было сделано:

1. **Проверка конфликтов бронирований** ✅
   - Автоматическая проверка при создании бронирования
   - API endpoint для проверки доступности

2. **Подбор соперника по уровню** ✅
   - Алгоритм совместимости (0-100 баллов)
   - Фильтры по уровню, городу, категориям
   - Отправка приглашений с push-уведомлениями
   - Требует подписку с feature `opponent_matching`

3. **Расширенная статистика** ✅
   - История бронирований
   - Активность по дням/часам
   - Метрики производительности
   - Достижения
   - Лидерборды
   - Требует подписку с feature `advanced_statistics`

4. **Система подписок** ✅
   - Модель `UserSubscription`
   - Декоратор `@require_feature` для защиты endpoints
   - API для управления подписками
   - Автоматическая проверка срока действия

---

## 🧪 Как протестировать

### 1. Backend запущен
```bash
cd /Users/tahyr/Documents/sportlink/backend
python3.11 manage.py runserver
```

### 2. Создайте тестовую подписку

Запустите скрипт для создания тестовой подписки пользователю:

```bash
cd /Users/tahyr/Documents/sportlink/backend
python3.11 -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.users.models import User
from apps.subscriptions.models import SubscriptionPlan
from apps.subscriptions.models_user import UserSubscription
from datetime import datetime, timedelta

# Получите пользователя (например, по номеру телефона)
user = User.objects.first()
print(f'User: {user.phone_number}')

# Получите план
plan = SubscriptionPlan.objects.first()
print(f'Plan: {plan.name}')

# Создайте подписку
subscription = UserSubscription(
    user=user,
    plan=plan,
    start_date=datetime.utcnow(),
    end_date=datetime.utcnow() + timedelta(days=30),
    status='active',
    amount_paid=plan.monthly_price,
    payment_method='test'
)
subscription.save()
print(f'✅ Subscription created: {subscription.id}')
"
```

### 3. Получите токен авторизации

```bash
# Войдите через админ панель или mobile приложение
# Скопируйте токен из localStorage или из ответа API
```

### 4. Тестируйте endpoints

#### Проверка доступности площадки:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/bookings/check-availability/?court_id=COURT_ID&start_time=2024-12-22T14:00:00Z&end_time=2024-12-22T16:00:00Z"
```

#### Поиск соперников:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/users/find-opponents/?limit=10"
```

#### Статистика:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/users/statistics/?range=30"
```

#### Достижения:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/users/achievements/"
```

#### Моя подписка:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/admin/subscriptions/my-subscription/"
```

#### Мои features:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/admin/subscriptions/my-features/"
```

### 5. Тест без подписки

Создайте нового пользователя без подписки и попробуйте:

```bash
curl -H "Authorization: Bearer NEW_USER_TOKEN" \
  "http://localhost:8000/api/v1/users/find-opponents/"
```

Должен вернуться HTTP 403:
```json
{
  "error": "Subscription required",
  "feature": "opponent_matching",
  "message": "This feature requires an active subscription"
}
```

---

## 📁 Созданные файлы

### Backend:
```
backend/apps/bookings/views.py                    - улучшенная проверка конфликтов
backend/apps/users/views_matching.py              - подбор соперников
backend/apps/users/views_statistics.py            - статистика и достижения
backend/apps/subscriptions/models_user.py         - модель UserSubscription
backend/apps/subscriptions/permissions.py         - декоратор @require_feature
backend/apps/subscriptions/views_user.py          - управление подписками
```

### Документация:
```
FEATURES_IMPLEMENTATION.md  - полная документация backend
FLUTTER_INTEGRATION.md      - примеры интеграции в Flutter
TESTING.md                  - этот файл
```

---

## 🎯 Следующие шаги

1. **Протестируйте все endpoints** через Postman или curl
2. **Интегрируйте в Flutter** используя примеры из `FLUTTER_INTEGRATION.md`
3. **Настройте платежную систему** для реальных подписок
4. **Добавьте webhook для автопродления** подписок

---

## 📞 Все готово!

Backend полностью готов к работе. Все features реализованы и защищены системой подписок.

**Запустите backend и начинайте тестировать!** 🚀

