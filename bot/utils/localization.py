import os

import yaml

from utils.config import config
from utils.logger import Logger

logger = Logger(__name__).get_logger()


class Localization:
    """
    Class responsible for managing translations in the bot.

    Loads translations from a YAML file and retrieves them based on a key and language.
    Logs any missing translations or errors.
    """

    def __init__(self) -> None:
        """
        Initializes the Localization class and loads the localization YAML file based on
        configuration settings.
        """
        self.localization_data = self._load_localization_file(config.loc.yaml_path)

    def _load_localization_file(self, file_path: str) -> dict:
        """
        Loads the localization YAML file into a dictionary.

        Args:
            file_path (str): The path to the localization file.

        Returns:
            dict: The dictionary containing localization data.
        """
        if not os.path.exists(file_path):
            logger.error(f"Localization file {file_path} not found.")
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                logger.info(f"Loading localization file: {file_path}")
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Failed to load localization file {file_path}: {e}")
            return {}

    def get_text(self, key: str, lang: str = None) -> str | dict:
        """
        Retrieves the translated text for the given key and language.

        Args:
            key (str): The key for the text to retrieve.
            lang (str): The language code (e.g., "EN", "RU"). Defaults to the configured
            default language.

        Returns:
            str | dict: The translated text. If it's a list, joins it into a single string. If it's
            a dictionary, returns the dictionary.
        """
        if lang:
            lang = lang.upper()

        if lang not in self.localization_data:
            lang = config.loc.default_lang

        try:
            keys = key.split(".")
            text = self.localization_data.get(lang, {})

            for k in keys:
                if text is None or not type(text) == dict:
                    logger.error(
                        f"Translation key '{key}' not found at '{k}' for language '{lang}'"
                    )
                    return f"[{key} not found]"
                text = text.get(k)

            if text is None:
                logger.error(f"Translation key '{key}' not found for language '{lang}'")
                return f"[{key}]"

            if type(text) == list:
                text = [item if item is not None else "" for item in text]
                return "\n".join(text)

            return text
        except Exception as e:
            logger.error(f"Error retrieving translation for key '{key}' in language '{lang}': {e}")
            return f"[{key}]"


localization = Localization()
