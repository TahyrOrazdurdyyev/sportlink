# Быстрый старт - Backend установлен! ✅

## Что уже сделано:

✅ Python 3.12 установлен  
✅ Виртуальное окружение создано (`venv`)  
✅ Django и все зависимости установлены  

## Следующие шаги:

### 1. Активировать виртуальное окружение (при каждом новом запуске):

В PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

В CMD:
```cmd
venv\Scripts\activate.bat
```

### 2. Настроить базу данных:

Создайте файл `.env` в папке `backend`:
```
DEBUG=True
SECRET_KEY=dev-secret-key-change-me
DATABASE_URL=sqlite:///db.sqlite3
```

Или используйте PostgreSQL через Docker:
```
DATABASE_URL=postgresql://sportlink:sportlink@localhost:5432/sportlink
```

### 3. Создать миграции:

```cmd
python manage.py makemigrations
```

### 4. Применить миграции:

```cmd
python manage.py migrate
```

### 5. Создать суперпользователя:

```cmd
python manage.py createsuperuser
```

### 6. Запустить сервер:

```cmd
python manage.py runserver
```

Сервер будет доступен по адресу: http://127.0.0.1:8000

## Важные команды:

- **Активировать venv**: `.\venv\Scripts\Activate.ps1`
- **Деактивировать venv**: `deactivate`
- **Установить новые пакеты**: `pip install package-name`
- **Посмотреть установленные пакеты**: `pip list`

## Полезные ссылки:

- Django Admin: http://127.0.0.1:8000/admin
- API Docs: http://127.0.0.1:8000/api/v1/

