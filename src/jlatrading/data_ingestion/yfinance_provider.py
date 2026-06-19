import pandas as pd
import yfinance as yf

from typing import Protocol

from .provider import MarketProvider
from ..common.app_logger import AppLogger

logger = AppLogger.get_logger(__name__)


class BaseYFinanceWrapper(Protocol):
    """Protocol for a wrapper around the yfinance library to allow for easier testing and abstraction."""
    def download(self, tickers: list[str], start: str, end: str, interval: str = "1d") -> pd.DataFrame | None:
        pass


class YFinanceWrapper(BaseYFinanceWrapper):
    def __init__(self):
        pass

    def download(self, tickers: list[str], start: str, end: str, interval: str = "1d") -> pd.DataFrame | None:
        return yf.download(tickers, start=start, end=end, interval=interval)


class YFinanceProvider(MarketProvider):
    """Market provider implementation using the yfinance library to fetch historical price data."""
    def __init__(self, yf_client: BaseYFinanceWrapper):
        self.yf = yf_client

    def download_daily_bar(self,
                           tickers: list[str],
                           start_date: str,
                           end_date: str) -> str:
        """
        Download historical price data for the specified tickers and date range using the yfinance library.
        Args:
            tickers: List of market tickers or tickers to query.
            start_date: Start date in "YYYY-MM-DD" format.
            end_date: End date in "YYYY-MM-DD" format.
        Returns:
            A json string representing the historical price data for the specified tickers and date range.
        """
        # data = yf.download(tickers, start=start_date, end=end_date, interval="1d", group_by='ticker').to_json(orient="records")
        yf = self.yf
        data = yf.download(tickers, start=start_date, end=end_date, interval="1d")
        if data is None:
            logger.d(f"No data found for tickers: {tickers} from {start_date} to {end_date}")
            return "[]"

        data = (
                data.stack(level="Ticker")
                .reset_index()
                .rename(columns={"level_1": "Ticker"})
                )

        json_str = data.rename(columns=str.lower).to_json(orient="records")
        print(data.head(5))
        logger.d(f"Downloaded data for tickers: {tickers} from {start_date} to {end_date}")
        if json_str is None:
            logger.d(f"No data found for tickers: {tickers} from {start_date} to {end_date}")
            return "[]"
        return json_str
