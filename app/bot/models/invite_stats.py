from dataclasses import dataclass, field
from typing import Dict


@dataclass
class InviteStats:
    revenue: Dict[str, float] = field(default_factory=dict)
    users_count: int = 0
    trial_users_count: int = 0
    paid_users_count: int = 0
    repeat_customers_count: int = 0
