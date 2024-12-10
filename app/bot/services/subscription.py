import json
import logging

from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _

logger = logging.getLogger(__name__)


class SubscriptionService:
    def __init__(self) -> None:
        """
        Initializes the SubscriptionService object.

        Loads plans and durations from the 'plans.json' file. The file must exist and contain
        properly structured data with "plans" and "durations" keys.
        """
        with open("plans.json", "r") as f:
            self.data = json.load(f)
        self.plans: list[dict] = self.data["plans"]
        self.durations: list[dict] = self.data["durations"]

    def get_plan(self, callback: str) -> dict | None:
        """
        Retrieves a plan based on the provided callback.

        Arguments:
            callback (str): The callback associated with the plan.

        Returns:
            dict | None: The plan as a dictionary if found, otherwise None.
        """
        for plan in self.plans:
            if plan["callback"] == callback:
                return plan
        logger.warning(f"Plan with callback '{callback}' not found.")
        return None

    def get_duration(self, callback: str) -> dict | None:
        """
        Retrieves a duration based on the provided callback.

        Arguments:
            callback (str): The callback associated with the duration.

        Returns:
            dict | None: The duration as a dictionary if found, otherwise None.
        """
        for duration in self.durations:
            if duration["callback"] == callback:
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

    async def get_selected_duration(self, state: FSMContext) -> dict:
        """
        Retrieves the selected duration from the FSM context.

        Arguments:
            state (FSMContext): The finite state machine context to retrieve data from.

        Returns:
            dict: The selected duration.

        Raises:
            ValueError: If the duration callback is missing or the duration is not found.
        """
        user_data = await state.get_data()
        duration_callback = user_data.get("duration_callback")
        if not duration_callback:
            logger.error("Duration callback is missing in state data.")
            raise ValueError("Duration callback is missing in state data.")
        duration = self.get_duration(duration_callback)
        if not duration:
            logger.error(
                f"Duration with callback '{duration_callback}' not found in available durations."
            )
            raise ValueError(f"Duration with callback '{duration_callback}' not found.")
        return duration

    def calculate_price(self, base_price: int, coefficient: float) -> int:
        """
        Calculates the total price based on the base price and coefficient.

        Arguments:
            base_price (int): The base price for the plan.
            coefficient (float): The duration coefficient.

        Returns:
            int: The calculated total price.

        Raises:
            ValueError: If either the coefficient or base price is less than or equal to zero.
        """
        if coefficient <= 0 or base_price <= 0:
            raise ValueError("Both coefficient and base price must be positive integers.")

        total_price = base_price * coefficient
        return int(total_price)

    def format_currency(self, currency: str) -> str:
        """
        Formats the currency symbol based on the provided currency code.

        Arguments:
            currency (str): The currency code (e.g., "RUB", "XTR", "USD").

        Returns:
            str: The formatted currency symbol (e.g., "₽", "★", "$").
                  If the currency code is unknown, it is returned unchanged.
        """
        if currency == "RUB":
            return "₽"
        elif currency == "XTR":
            return "★"
        elif currency == "USD":
            return "$"
        return currency

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
