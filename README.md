# Документация по запуску проекта

## Пререквизиты

* Python 3.11+
* pip
* virtualenv (optional, но рекомендуется)
* PostgreSQL/или SQLite (SQLite по умолчанию)

---

## 1. Склонировать репозиторий

```bash
git clone <ссылка на репо>
cd <папка проекта>
```

---

## 2. Создать виртуальное окружение (опционально)

```bash
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
.venv\Scripts\activate       # Windows
```

---

## 3. Установить зависимости

```bash
pip install -r requirements.txt
```

---

## 4. Настройка .env

Создать файл `.env` в корне проекта с следующим содержимым:

```
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=587
EMAIL_HOST_USER=primer@yandex.ru
EMAIL_HOST_PASSWORD=<пароль приложения>
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=primer@yandex.ru
```

---

## 5. Миграции базы данных

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 6. Создать администратора

```bash
python manage.py createsuperuser
```

---

## 7. Запуск сервера

```bash
python manage.py runserver
```

---

## 8. Доступы:

* Админка: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
* API: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)...

---

## 9. Тестовые запросы

Можно выполнять через Postman/файл `requests.http`, приложенный к проекту. 

Менять статус заказа может только администратор. Для обращению к API используйте токены, которые можно получить в админке или при регистрации пользователя.
Я с VPN сижу, поэтому при регистрации довольно долго приходит письмо с подтверждением. Если не приходит, проверьте настройки SMTP в `.env`. В любом случае сейчас настроено, чтобы сообщение просто выводилось в терминал.




