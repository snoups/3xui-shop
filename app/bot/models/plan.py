from dataclasses import dataclass, field


@dataclass
class Prices:
    rub: dict[int, float] = field(default_factory=dict)
    usd: dict[int, float] = field(default_factory=dict)
    xtr: dict[int, float] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Prices":
        return cls(
            rub={int(k): v for k, v in data.get("RUB", {}).items()},
            usd={int(k): v for k, v in data.get("USD", {}).items()},
            xtr={int(k): v for k, v in data.get("XTR", {}).items()},
        )

    def to_dict(self) -> dict:
        prices_dict = {
            "RUB": {str(k): v for k, v in self.rub.items()},
            "USD": {str(k): v for k, v in self.usd.items()},
            "XTR": {str(k): v for k, v in self.xtr.items()},
        }
        return prices_dict


@dataclass
class Plan:
    devices: int
    prices: Prices

    @classmethod
    def from_dict(cls, data: dict) -> "Plan":
        return cls(
            devices=data["devices"],
            prices=Prices.from_dict(data["prices"]),
        )

    def to_dict(self) -> dict:
        plan_dict = {
            "devices": self.devices,
            "prices": self.prices.to_dict(),
        }
        return plan_dict
