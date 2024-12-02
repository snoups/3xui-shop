import json

from bot.utils.config import config
from bot.utils.logger import Logger

logger = Logger(__name__).get_logger()


def get(callback=None) -> list | dict:
    """
    Retrieves a list of available subscription plans or a specific plan by its callback.

    Args:
        callback (str, optional): The callback value to filter the plan. If not provided,
                                  all plans are returned.

    Returns:
        list | dict: If no callback is provided, returns a list of all subscription plans. If a
                     callback is provided, returns a dictionary of the corresponding plan. If no
                     plan matches the callback, returns an empty dictionary.
    """
    with open("bot/subscriptions.json") as file:
        data = json.load(file)
    if callback is None:
        return data["plans"]
    for plan in data["plans"]:
        if plan["callback"] == callback:
            return plan
    return dict()


def get_coefficients(period: None | int = None) -> dict | float:
    """
    Retrieves subscription price coefficients for all periods or a specific period.

    Args:
        period (int, optional): The subscription period (in days). If not provided, coefficients
                                for all periods are returned.

    Returns:
        dict | float: If no period is provided, returns a dictionary of coefficients for all
                      periods. If a period is provided, returns the coefficient for the
                      specified period.
    """
    with open("bot/subscriptions.json") as file:
        data = json.load(file)
    if period is None:
        return data["coefficients"]
    return data["coefficients"][str(period)]
