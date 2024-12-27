import json
import logging
import os
from dataclasses import dataclass, field

from aiogram.utils.i18n import gettext as _

from app.bot.services.client import UNLIMITED
from app.config import DEFAULT_PLANS_DIR

logger = logging.getLogger(__name__)


@dataclass
class Prices:
    """
    Represents pricing data for different currencies.

    Attributes:
        rub (dict[int, float]): Prices in Russian Rubles.
        usd (dict[int, float]): Prices in US Dollars.
        xtr (dict[int, float]): Prices in XTR.
    """

    rub: dict[int, float] = field(default_factory=dict)
    usd: dict[int, float] = field(default_factory=dict)
    xtr: dict[int, float] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Prices":
        """
        Create a Prices instance from a dictionary.

        Arguments:
            data (dict): Dictionary containing price data by currency.

        Returns:
            Prices: An instance of Prices with parsed data.
        """
        return cls(
            rub={int(k): v for k, v in data.get("RUB", {}).items()},
            usd={int(k): v for k, v in data.get("USD", {}).items()},
            xtr={int(k): v for k, v in data.get("XTR", {}).items()},
        )

    def to_dict(self) -> dict:
        """
        Convert Prices instance to dictionary.

        Returns:
            dict: Dictionary representation of the Prices instance.
        """
        prices_dict = {
            "RUB": {str(k): v for k, v in self.rub.items()},
            "USD": {str(k): v for k, v in self.usd.items()},
            "XTR": {str(k): v for k, v in self.xtr.items()},
        }
        return prices_dict


@dataclass
class Plan:
    """
    Represents a subscription plan.

    Attributes:
        devices (int): The number of devices supported by the plan.
        prices (Prices): The pricing information for this plan.
    """

    devices: int
    prices: Prices

    @classmethod
    def from_dict(cls, data: dict) -> "Plan":
        """
        Create a Plan instance from a dictionary.

        Arguments:
            data (dict): Dictionary containing plan data.

        Returns:
            Plan: An instance of Plan with parsed data.
        """
        return cls(
            devices=data["devices"],
            prices=Prices.from_dict(data["prices"]),
        )

    def to_dict(self) -> dict:
        """
        Convert Plan instance to dictionary.

        Returns:
            dict: Dictionary representation of the Plan instance.
        """
        plan_dict = {
            "devices": self.devices,
            "prices": self.prices.to_dict(),
        }
        return plan_dict


class PlansService:
    """
    Provides plans data and utilities for handling subscription plans and pricing.

    Loads plans configurations from a JSON file and provides methods to interact with
    the plan data, such as getting a plan by device count, calculating prices,
    and converting device count/duration to readable formats.
    """

    def __init__(self) -> None:
        """
        Initializes the PlanService and loads the plans from a JSON file.

        Raises:
            FileNotFoundError: If the 'plans.json' file does not exist.
            ValueError: If the JSON data is malformed or missing expected keys.
        """
        file_path = DEFAULT_PLANS_DIR

        if not os.path.isfile(file_path):
            logger.error(f"The file '{file_path}' does not exist.")
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        try:
            with open(file_path, "r") as f:
                self.data = json.load(f)
            logger.info(f"Loaded plans data from '{file_path}'.")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse the file '{file_path}'. Invalid JSON format.")
            raise ValueError(f"The file '{file_path}' is not a valid JSON file.")

        if "plans" not in self.data or not isinstance(self.data["plans"], list):
            logger.error(f"The 'plans' key is missing or not a list in '{file_path}'.")
            raise ValueError(f"The 'plans' key is missing or not a list in '{file_path}'.")

        if "durations" not in self.data or not isinstance(self.data["durations"], list):
            logger.error(f"The 'durations' key is missing or not a list in '{file_path}'.")
            raise ValueError(f"The 'durations' key is missing or not a list in '{file_path}'.")

        self.plans: list[Plan] = [Plan.from_dict(plan) for plan in self.data["plans"]]
        self.durations: list[int] = self.data["durations"]
        logger.info("Plans and durations loaded successfully.")

    def get_plan(self, devices: int) -> Plan | None:
        """
        Get the plan with a specific device count.

        Arguments:
            devices (int): The device count to search for.

        Returns:
            Plan | None: The plan matching the device count or None if not found.
        """
        logger.debug(f"Searching for plan with devices: {devices}")
        plan = next((plan for plan in self.plans if plan.devices == devices), None)
        if plan:
            logger.debug(f"Found plan with {devices} devices")
        else:
            logger.warning(f"Plan with {devices} devices not found.")
        return plan

    @staticmethod
    def get_price_for_duration(prices: dict, duration: int, currency: str = "RUB") -> float:
        """
        Get the price for a specific duration and currency.

        Arguments:
            prices (dict): The prices dictionary.
            duration (int): The duration in days.
            currency (str): The currency to get the price for (default is 'RUB').

        Returns:
            float: The price for the specified duration and currency.
        """
        price = prices.get(currency, {}).get(str(duration), 0.0)
        logger.debug(f"Price for {duration} days in {currency} currency: {price}")
        return price

    @staticmethod
    def convert_devices_to_title(devices: int) -> str:
        """
        Convert the device count to a human-readable string.

        Arguments:
            devices (int): The number of devices supported by the plan.

        Returns:
            str: The device count in a readable format.
        """
        if devices == -1:
            logger.debug("Devices count is unlimited.")
            return UNLIMITED + _("devices")
        logger.debug(f"Converted devices {devices} to string")
        return _("1 device", "{} devices", devices).format(devices)

    @staticmethod
    def convert_days_to_period(days: int) -> str:
        """
        Convert the number of days to a human-readable period.

        Arguments:
            days (int): The duration in days.

        Returns:
            str: The duration in a readable format, such as "1 year", "3 months", etc.
        """
        if days == -1:
            logger.debug("Duration is unlimited.")
            return UNLIMITED

        if days % 365 == 0:
            years = days // 365
            logger.debug(f"Converted {days} days to {years} years.")
            return _("1 year", "{} years", years).format(years)

        if days % 30 == 0:
            months = days // 30
            logger.debug(f"Converted {days} days to {months} months.")
            return _("1 month", "{} months", months).format(months)

        logger.debug(f"Converted {days} days to string.")
        return _("1 day", "{} days", days).format(days)
