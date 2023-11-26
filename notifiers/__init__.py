from .BaseNotifier import BaseNotifier
from .TelegramNotifier import TelegramNotifier


notifiers = {
    'telegram_bot': TelegramNotifier
}


def get_notifier(broker: str, params: dict) -> BaseNotifier | None:
    notifier_class = notifiers.get(broker)
    if notifier_class:
        return notifier_class(**params)
