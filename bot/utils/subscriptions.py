import json

from bot.utils.config import config
from bot.utils.logger import Logger

logger = Logger(__name__).get_logger()


def get(callback=None) -> list | dict:
    with open("subscriptions.json") as file:
        data = json.load(file)
    if callback is None:
        return data["plans"]
    for plan in data["plans"]:
        if plan["callback"] == callback:
            return plan
    return dict()


def get_coefficients(period: None | int = None) -> dict | float:
    with open("subscriptions.json") as file:
        data = json.load(file)
    if period is None:
        return data["coefficients"]
    return data["coefficients"][str(period)]
