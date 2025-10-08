# Course Work 4 — Система рассылок

## Описание

Проект реализует систему управления клиентами, сообщений и рассылок. Основные функции:  

- CRUD для клиентов и сообщений.  
- Создание, редактирование, удаление и запуск рассылок.  
- Отправка рассылок через интерфейс и командную строку.  
- Статистика и отчеты по рассылкам.  
- Кеширование списков и статистики с помощью Redis.  
- Поддержка ролей пользователей (менеджер/обычный пользователь).  

---

## Требования

- Python 3.13+  
- Django 5.2+  
- PostgreSQL  
- Redis  
- Виртуальное окружение (рекомендуется)

---

## Установка

1. Клонировать репозиторий:

```bash
git clone <репозиторий>
cd Course_Work_4
```

2. Создать виртуальное окружение и активировать его:

Создайте виртуальное окружение и активируйте его:

```bash
# Linux / macOS
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

3. Установите зависимости:
```
pip install -r requirements.txt
```

4. Настройка .env

Создайте файл .env в корне проекта:
```
SECRET_KEY="your-secret-key"
DEBUG=True
ALLOWED_HOSTS="127.0.0.1,localhost"

DB_NAME="course_work_4_db"
DB_USER="postgres"
DB_PASSWORD="your_db_password"
DB_HOST="127.0.0.1"
DB_PORT="5432"

EMAIL_HOST_USER="your_email@gmail.com"
EMAIL_HOST_PASSWORD="your_app_password"
```
Для Gmail используйте App Password вместо обычного пароля.

5. Настройка базы данных

- Создайте базу данных PostgreSQL.
- Примените миграции:
```
python manage.py migrate
```
6. Создание суперпользователя
```
python manage.py createsuperuser
```

Следуйте инструкциям для задания email и пароля.
7. Запуск проекта
```
python manage.py runserver
```

Перейдите по адресу: http://127.0.0.1:8000

8. Используемые приложения

- clients – управление клиентами (Recipient)
- messages_app – создание и редактирование сообщений (Message)
- mailings – рассылки сообщений выбранным клиентам (Mailing, MailingAttempt)
- users – управление пользователями и ролями

9. Основной функционал.

Клиенты

- Создание, редактирование и удаление клиентов
- Кеширование списка клиентов (Redis)
- Разграничение доступа: менеджеры видят всех, обычные пользователи – только свои записи

Сообщения

- Создание, редактирование и удаление сообщений
- Кеширование списка сообщений (Redis)
- Разграничение доступа по владельцу

Рассылки

- Создание рассылок с выбором сообщений и получателей
- Отправка рассылки через интерфейс
- Отправка рассылки через команду Django (manage.py send_mailing)
- Статистика по рассылкам: успешные/неуспешные попытки, уникальные получатели
- Кеширование статистики (Redis)

10. Кэширование

- Используется Redis для кеширования списка клиентов, сообщений и статистики рассылок.
- Настройка в settings.py:
```
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    }
}
```
11. Настройка email

- Для разработки используется console.EmailBackend (письма выводятся в консоль).
- Для отправки реальных писем укажите настройки SMTP в .env и settings.py:
```
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```
12. Логирование

- Все попытки отправки писем логируются в logs/app.log.
- Успешные и неуспешные попытки рассылки сохраняются в базе (MailingAttempt).

13. Роли пользователей

- Менеджеры – видят всех клиентов и рассылки, могут редактировать и удалять любые объекты.
- Обычные пользователи – видят и редактируют только свои объекты.

12. Команды Django

- Создать суперпользователя:
```
python manage.py createsuperuser
```

- Отправить рассылку через командную строку:
```
python manage.py send_mailing <mailing_id>
```
13. Примечания

- Перед использованием Redis убедитесь, что сервер запущен: 
```redis-server```

- Для Gmail необходимо включить App Password, иначе SMTP не будет работать.

## Лицензия

Проект используется в образовательных целях.