import json
import logging
import os

from app.bot.models import Plan
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

        self._plans: list[Plan] = [Plan.from_dict(plan) for plan in self.data["plans"]]
        self._durations: list[int] = self.data["durations"]
        logger.info("Plans loaded successfully.")

    def get_plan(self, devices: int) -> Plan | None:
        plan = next((plan for plan in self._plans if plan.devices == devices), None)

        if not plan:
            logger.critical(f"Plan with {devices} devices not found.")

        return plan

    def get_all_plans(self) -> list[Plan]:
        return self._plans

    def get_durations(self) -> list[int]:
        return self._durations
