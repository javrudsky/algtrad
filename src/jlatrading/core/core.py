from ..common.app_logger import AppLogger
from ..common.config import AppConfig
from ..common.utils import DateUtils as du
from ..common.utils import DateFormat
from .comp_factory import ComponentFactory as cf


def setup():
    AppConfig.load_config()
    log_level = AppConfig.get_value("LOG_LEVEL", default="INFO")
    AppLogger.setup_logging(log_file=AppConfig.get_value("LOG_PATH", default=None), level=log_level)
    logger = AppLogger.get_logger(__name__)
    logger.i("Application setup complete.")


def download_daily_bar(tickers: list[str], start_date: str = "", end_date: str = "") -> int:
    if not tickers:
        raise ValueError("tickers must not be empty.")

    if any(not isinstance(ticker, str) or not ticker.strip() for ticker in tickers):
        raise ValueError("All tickers must be non-empty strings.")

    if start_date and not du.is_valid_yyyymmdd_str(start_date):
        raise ValueError(f"Invalid start_date format. Expected {DateFormat.YYYYMMDD_FORMAT}.")

    if end_date and not du.is_valid_yyyymmdd_str(end_date):
        raise ValueError(f"Invalid end_date format. Expected {DateFormat.YYYYMMDD_FORMAT}.")

    if not du.is_valid_date_range(start_date, end_date):
        raise ValueError("Start date must be less than or equal to end date.")

    market_service = cf.build_market_service()
    return market_service.download_daily_bar(tickers, start_date=start_date, end_date=end_date)


def download_instruments_prices() -> int:
    market_service = cf.build_market_service()
    return market_service.download_instruments_prices()
