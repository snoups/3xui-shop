import json
import logging
from datetime import datetime, timedelta, timezone

from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from py3xui import AsyncApi, Client
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.navigation import NavigationAction
from app.db.models.user import User

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    Service for managing subscription plans and durations.
    """

    def __init__(self) -> None:
        """
        Initializes the SubscriptionService object.

        Loads plans and durations from the 'plans.json' file. The file must exist and contain
        properly structured data with "plans" and "durations" keys.
        """
        with open("plans.json", "r") as f:
            self.data = json.load(f)
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

    async def set_selected_plan(self, state: FSMContext, plan_callback: str) -> None:
        """
        Saves the selected plan callback to the FSM context.

        Arguments:
            state (FSMContext): The finite state machine context to store data.
            plan_callback (str): The callback of the selected plan.
        """
        await state.update_data(plan_callback=plan_callback)

    async def set_selected_duration(self, state: FSMContext, duration_callback: str) -> None:
        """
        Saves the selected duration callback to the FSM context.

        Arguments:
            state (FSMContext): The finite state machine context to store data.
            duration_callback (str): The callback of the selected duration.
        """
        await state.update_data(duration_callback=duration_callback)

    async def get_selected_plan(self, state: FSMContext) -> dict:
        """
        Retrieves the selected plan from the FSM context.

        Arguments:
            state (FSMContext): The finite state machine context to retrieve data from.

        Returns:
            dict: The selected plan.

        Raises:
            ValueError: If the plan callback is missing or the plan is not found.
        """
        user_data = await state.get_data()
        plan_callback = user_data.get("plan_callback")
        if not plan_callback:
            logger.error("Plan callback is missing in state data.")
            raise ValueError("Plan callback is missing in state data.")
        plan = self.get_plan(plan_callback)
        if not plan:
            logger.error(f"Plan with callback '{plan_callback}' not found in available plans.")
            raise ValueError(f"Plan with callback '{plan_callback}' not found.")
        return plan

    async def get_selected_duration(self, state: FSMContext) -> int:
        """
        Retrieves the selected duration from the FSM context.

        Arguments:
            state (FSMContext): The finite state machine context to retrieve data from.

        Returns:
            int: The selected duration.

        Raises:
            ValueError: If the duration callback is missing or the duration is not found.
        """
        user_data = await state.get_data()
        duration_callback = user_data.get("duration_callback")
        if not duration_callback:
            logger.error("Duration callback is missing in state data.")
            raise ValueError("Duration callback is missing in state data.")
        duration = self.get_duration(duration_callback)
        if duration is None:
            logger.error(
                f"Duration with callback '{duration_callback}' not found in available durations."
            )
            raise ValueError(f"Duration with callback '{duration_callback}' not found.")
        return duration

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
            return "∞"
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
            return "∞"

        if days % 365 == 0:
            years = days // 365
            return _("1 year", "{} years", years).format(years)

        if days % 30 == 0:
            months = days // 30
            return _("1 month", "{} months", months).format(months)

        return _("1 day", "{} days", days).format(days)

    def gb_to_bytes(self, traffic_gb: int) -> int:
        """
        Convert traffic volume from gigabytes (GB) to bytes.

        Arguments:
            traffic_gb (float): The traffic volume in gigabytes.

        Returns:
            int: The traffic volume in bytes.
        """
        bytes_in_gb = 1024**3  # 1 GB = 1024^3 bytes
        return int(traffic_gb * bytes_in_gb)

    def days_to_unix_milliseconds(self, days: int) -> int:
        """
        Convert a number of days to a Unix timestamp in milliseconds.

        Arguments:
            days (int): Number of days to convert.

        Returns:
            int: Unix timestamp in milliseconds.
        """
        now = datetime.now(timezone.utc)
        target_time = now + timedelta(days=days)
        unix_timestamp_seconds = int(target_time.timestamp())
        unix_timestamp_milliseconds = unix_timestamp_seconds * 1000
        return unix_timestamp_milliseconds

    async def create_subscription(self, session: AsyncSession, api: AsyncApi, data: dict) -> None:
        user: User = await User.get(session, user_id=data["user_id"])
        new_client = Client(
            id=user.vpn_id,
            email=str(user.user_id),
            enable=True,
            limitIp=3,
            totalGB=self.gb_to_bytes(data["traffic"]),
            expiryTime=self.days_to_unix_milliseconds(data["duration"]),
            flow="xtls-rprx-vision",
        )
        inbound_id = 7
        await api.client.add(inbound_id, [new_client])
