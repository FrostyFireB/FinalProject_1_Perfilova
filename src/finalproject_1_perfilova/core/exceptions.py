class InsufficientFundsError(Exception):
    """Недостаточно средств для операции."""
    pass


class WalletNotFoundError(Exception):
    """Кошелёк (валюта) не найден в портфеле."""
    pass


class CurrencyNotFoundError(Exception):
    """Неизвестный/неподдерживаемый код валюты."""
    pass


class ApiRequestError(Exception):
    """Сбой при обращении к внешнему API (Parser Service/заглушка)."""

    def __init__(self, reason: str):
        super().__init__(f"Ошибка при обращении к внешнему API: {reason}")
        self.reason = reason