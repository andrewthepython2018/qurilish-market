import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_order_notification(order):
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.info("Telegram notification skipped: token or chat id is not configured.")
        return False
    text = (
        "Новая заявка Qurilish Market\n\n"
        f"Товар: {order.product.name}\n"
        f"Количество: {order.quantity} {order.product.unit}\n"
        f"Клиент: {order.customer_name}\n"
        f"Телефон: {order.phone}\n"
        f"Город: {order.city or '-'}\n"
        f"Комментарий: {order.comment or '-'}"
    )
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={"chat_id": settings.TELEGRAM_CHAT_ID, "text": text}, timeout=8)
        response.raise_for_status()
        return True
    except requests.RequestException:
        logger.exception("Telegram notification failed for order %s", order.pk)
        return False
