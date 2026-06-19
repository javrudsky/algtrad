import logging
import sys
from pathlib import Path


class AppLogger:
    """
    Wrapper around the standard logging module to provide a consistent interface for logging in the application.
    Using just a simple wrapper allows us to easily switch to a different logging library in the future if needed, without changing the rest of the codebase.
    """
    def __init__(self, module_name: str, _internal: bool = False) -> None:
        if not _internal:
            raise RuntimeError("Use MyClass.create() instead")
        self.logger = logging.getLogger(module_name)

    def d(self, message: str) -> None:
        self.logger.debug(message)

    def i(self, message: str) -> None:
        self.logger.info(message)

    def w(self, message: str) -> None:
        self.logger.warning(message)

    def e(self, message: str) -> None:
        self.logger.error(message)

    def ex(self, message: str) -> None:
        self.logger.exception(message)

    def c(self, message: str) -> None:
        self.logger.critical(message)

    @classmethod
    def get_logger(cls, module_name: str) -> "AppLogger":
        return cls(module_name, _internal=True)

    @staticmethod
    def __map_log_level(value: str) -> int:
        levels = {
            "CRITICAL": logging.CRITICAL,
            "FATAL": logging.FATAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "WARN": logging.WARN,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET,
            "NONE": logging.NOTSET,
        }

        key = value.strip().upper()
        if key not in levels:
            logging.getLogger(__name__).warning(f"Invalid log level: {value}. Defaulting to NONE.")
            return logging.NOTSET

        return levels[key]

    @staticmethod
    def setup_logging(log_file: str | None = None, level: str = "NONE") -> None:
        log_level = AppLogger.__map_log_level(level)

        handler: logging.Handler
        if log_file:
            # Creates the whole path if it doesn't exist, so that the FileHandler can create the log file without issues.
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(log_file)
        else:
            handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)

        root = logging.getLogger()
        root.setLevel(log_level)
        root.handlers.clear()
        root.addHandler(handler)
