from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.bot.services import (
        NotificationService,
        PlanService,
        ServerPoolService,
        VPNService,
    )

from dataclasses import dataclass


@dataclass
class ServicesContainer:
    server_pool: ServerPoolService
    plan: PlanService
    vpn: VPNService
    notification: NotificationService
