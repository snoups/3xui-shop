from dataclasses import dataclass
from typing import Any

from app.bot.utils.constants import Currency


@dataclass
class Plan:
    devices: int
    prices: dict[str, dict[int, float]]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Plan":
        return cls(
            devices=data["devices"],
            prices={k: {int(m): p for m, p in v.items()} for k, v in data["prices"].items()},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "devices": self.devices,
            "prices": {k: {str(m): p for m, p in v.items()} for k, v in self.prices.items()},
        }

    def get_price(self, currency: Currency | str, duration: int) -> float:
        if isinstance(currency, str):
            currency = Currency.from_code(currency)

        return self.prices[currency.code][duration]
