import json
import logging
import os

from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.navigation import NavigationAction
from app.bot.services.client import UNLIMITED
from app.bot.services.vpn import VPNService
from app.db.models.user import User

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    Service for managing subscription plans, durations, and traffic.

    This service provides methods for handling subscription plans, durations,
    traffic conversion, and creating new subscriptions. It reads subscription plans
    and durations from a JSON file ('plans.json') and offers utility methods to
    generate callbacks, calculate prices, and convert data to human-readable formats.

    Attributes:
        plans (list[dict]): List of subscription plans.
        durations (list[int]): List of available subscription durations.
    """

    def __init__(self, session: AsyncSession, vpn: VPNService) -> None:
        """
        Initializes the SubscriptionService object.

        Loads plans and durations from the 'plans.json' file. The file must exist and contain
        properly structured data with "plans" and "durations" keys.

        Arguments:
            session (AsyncSession): The database session used for user operations.
            vpn (VPNService): The VPN service instance used for interacting with the VPN.

        Raises:
            FileNotFoundError: If 'plans.json' file does not exist.
            ValueError: If 'plans.json' file is not a valid JSON file or has an incorrect structure.
        """
        self.session = session
        self.vpn = vpn
        file_path = "plans.json"

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        try:
            with open(file_path, "r") as f:
                self.data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"The file '{file_path}' is not a valid JSON file.")

        # Validate the file structure
        if "plans" not in self.data or not isinstance(self.data["plans"], list):
            raise ValueError(f"The 'plans' key is missing or not a list in '{file_path}'.")

        if "durations" not in self.data or not isinstance(self.data["durations"], list):
            raise ValueError(f"The 'durations' key is missing or not a list in '{file_path}'.")

        self.plans: list[dict] = self.data["plans"]
        self.durations: list[int] = self.data["durations"]

    def generate_plan_callback(self, traffic: int) -> str:
        """
        Generates a callback string for the plan based on traffic.

        Arguments:
            traffic (int): The traffic value in GB.

        Returns:
            str: A callback string for the plan, such as 'traffic_50'.
        """
        return NavigationAction.TRAFFIC + f"_{traffic}"

    def generate_duration_callback(self, duration: int) -> str:
        """
        Generates a callback string for the duration.

        Arguments:
            duration (int): The duration in days.

        Returns:
            str: A callback string for the duration, such as 'duration_30'.
        """
        return NavigationAction.DURATION + f"_{duration}"

    def get_plan(self, callback: str) -> dict | None:
        """
        Retrieves a plan based on the provided callback.

        Arguments:
            callback (str): The callback associated with the plan.

        Returns:
            dict | None: The plan as a dictionary if found, otherwise None.
        """
        for plan in self.plans:
            if callback == self.generate_plan_callback(plan["traffic"]):
                return plan
        logger.warning(f"Plan with callback '{callback}' not found.")
        return None

    def get_duration(self, callback: str) -> int | None:
        """
        Retrieves a duration based on the provided callback.

        Arguments:
            callback (str): The callback associated with the duration.

        Returns:
            int | None: The duration if found, otherwise None.
        """
        for duration in self.durations:
            if self.generate_duration_callback(duration) == callback:
                return duration
        logger.warning(f"Duration with callback '{callback}' not found.")
        return None

    def get_price_for_duration(self, prices: dict, duration: int, currency: str = "RUB") -> int:
        """
        Retrieves the price for a given duration and currency.

        Arguments:
            prices (dict): Dictionary with prices for different durations and currencies.
            duration (int): Duration in days for which the price is needed.
            currency (str): Currency code (default is 'RUB').

        Returns:
            int: Price for the specified duration and currency.
        """
        return prices[currency][str(duration)]

    def convert_traffic_to_title(self, traffic: int) -> str:
        """
        Converts the given traffic value to a human-readable title.

        If the traffic is -1, it returns the symbol for infinity (∞), otherwise
        it returns the traffic value with the unit "GB".

        Arguments:
            traffic (int): The traffic value in GB.
                Use -1 to represent infinite traffic.

        Returns:
            str: A string representation of traffic, such as "10 GB" or "∞" for infinite traffic.
        """
        if traffic == -1:
            return UNLIMITED
        else:
            return str(traffic) + " " + _("GB")

    def convert_days_to_period(self, days: int) -> str:
        """
        Converts the given number of days into a human-readable period.

        Supports days, months, and years, as well as localization via ngettext.

        Arguments:
            days (int): The number of days to convert. Use -1 to represent infinity.

        Returns:
            str: A string representation of the period (e.g., "1 day", "2 months", "5 years").
                 Returns "∞" for infinite duration.
        """
        if days == -1:
            return UNLIMITED

        if days % 365 == 0:
            years = days // 365
            return _("1 year", "{} years", years).format(years)

        if days % 30 == 0:
            months = days // 30
            return _("1 month", "{} months", months).format(months)

        return _("1 day", "{} days", days).format(days)

    async def create_subscription(
        self,
        user_id: int,
        traffic: int,
        duration: int,
    ) -> None:
        """
        Creates a new subscription for the user.

        Arguments:
            user_id (int): The user ID for whom the subscription is being created.
            traffic (int): The amount of traffic for the user in GB.
            duration (int): The duration of the subscription in days.
        """
        async with self.session() as session:
            user: User = await User.get(session, user_id=user_id)
        # TODO: make receiving a subscription link
        if await self.vpn.is_client_exists(user.user_id):
            await self.vpn.update_client(user, traffic, duration)
        else:
            await self.vpn.create_client(user, traffic, duration)
