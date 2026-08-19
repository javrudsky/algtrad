from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)


class TypedValue:
    def __init__(self, value):
        self.value = value

    def to_int(self, default=0) -> int:
        try:
            return int(self.value)
        except (ValueError, TypeError):
            return default

    def to_str(self, default: str = "") -> str:
        if self.value is None:
            logger.debug(f"Value is None, returning default: {default}")
            return default
        if isinstance(self.value, str):
            return self.value
        logger.debug(f"Incorrect config value type, returning: {default}")
        return default

    def to_strlist(self, default: list[str] | None = None) -> list[str]:
        default = [] if default is None else default
        if self.value is None:
            logger.debug(f"Value is None, returning default: {default}")
            return default
        if isinstance(self.value, str):
            return [item.strip() for item in self.value.split(",")]

        logger.debug(f"Incorrect config value type, returning: {default}")
        return default


class AppConfig():

    @staticmethod
    def load_config():
        file_path = os.getenv("ALGTRAD_PATH", "")
        if not file_path:
            logger.warning("ALGTRAD_PATH environment variable is not set. Skipping loading .env file.")
            return
        load_dotenv(file_path + ".env")

    @staticmethod
    def get_value(key: str, default=None) -> str | None:
        return os.getenv(key, default)

    @staticmethod
    def get_typed_value(key: str, default=None) -> TypedValue:
        value = AppConfig.get_value(key, default)
        return TypedValue(value)
