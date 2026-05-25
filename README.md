# Qurilish Market MVP

Рабочий Django MVP: каталог строительных материалов, категории, карточка товара, форма заявки, Django Admin и Telegram-уведомление менеджеру.

## Быстрый старт

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Откройте `http://127.0.0.1:8000/`.

## Telegram

Создайте бота через BotFather и задайте переменные окружения:

```powershell
$env:TELEGRAM_BOT_TOKEN="..."
$env:TELEGRAM_CHAT_ID="..."
```

После этого новая заявка будет сохраняться в базе и отправляться в Telegram.

## Основные URL

- `/` — главная
- `/catalog/` — каталог
- `/category/<slug>/` — категория
- `/product/<slug>/` — карточка товара
- `/order/<product_id>/` — форма заявки
- `/admin/` — админка
