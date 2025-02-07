import json
import logging
import os

from aiogram.utils.i18n import gettext as _

from app.bot.models import Plan
from app.bot.utils.constants import UNLIMITED
from app.config import DEFAULT_PLANS_DIR

logger = logging.getLogger(__name__)


class PlanService:
    def __init__(self) -> None:
        file_path = DEFAULT_PLANS_DIR

        if not os.path.isfile(file_path):
            logger.error(f"File '{file_path}' does not exist.")
            raise FileNotFoundError(f"File '{file_path}' does not exist.")

        try:
            with open(file_path, "r") as f:
                self.data = json.load(f)
            logger.info(f"Loaded plans data from '{file_path}'.")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse file '{file_path}'. Invalid JSON format.")
            raise ValueError(f"File '{file_path}' is not a valid JSON file.")

        if "plans" not in self.data or not isinstance(self.data["plans"], list):
            logger.error(f"'plans' key is missing or not a list in '{file_path}'.")
            raise ValueError(f"'plans' key is missing or not a list in '{file_path}'.")

        if "durations" not in self.data or not isinstance(self.data["durations"], list):
            logger.error(f"'durations' key is missing or not a list in '{file_path}'.")
            raise ValueError(f"'durations' key is missing or not a list in '{file_path}'.")

        self.plans: list[Plan] = [Plan.from_dict(plan) for plan in self.data["plans"]]
        self.durations: list[int] = self.data["durations"]
        logger.info("Plans loaded successfully.")

    def get_plan(self, devices: int) -> Plan | None:
        plan = next((plan for plan in self.plans if plan.devices == devices), None)

        if not plan:
            logger.critical(f"Plan with {devices} devices not found.")

        return plan

    @staticmethod
    def get_price_for_duration(prices: dict, duration: int, currency: str = "RUB") -> float:
        price = prices.get(currency, {}).get(str(duration), 0)
        return price

    @staticmethod
    def convert_devices_to_title(devices: int) -> str:
        if devices == -1:
            return UNLIMITED + _("devices")
        return _("1 device", "{} devices", devices).format(devices)

    @staticmethod
    def convert_days_to_period(days: int) -> str:
        if days == -1:
            return UNLIMITED

        if days % 365 == 0:
            years = days // 365
            return _("1 year", "{} years", years).format(years)

        if days % 30 == 0:
            months = days // 30
            return _("1 month", "{} months", months).format(months)

        return _("1 day", "{} days", days).format(days)
