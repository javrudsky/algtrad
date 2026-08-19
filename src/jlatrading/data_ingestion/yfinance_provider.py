import pandas as pd
import yfinance as yf

from typing import Protocol

from .provider import MarketProvider
from ..common.app_logger import AppLogger
from ..common.utils import DateUtils

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
                           end_date: str) -> list[dict]:
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
        # Adding ".BA" suffix to each ticker for yfinance compatibility
        tickers = [f"{ticker}.BA" for ticker in tickers]
        data = yf.download(tickers, start=start_date, end=end_date, interval="1d")
        if data is None or data.empty:
            logger.d(f"No data found for tickers: {tickers} from {start_date} to {end_date}")
            return []

        data = (
                data.stack(level="Ticker")
                .reset_index()
                .rename(columns={"level_1": "Ticker"})
                )

        # Adding this line to ensure only fieds available in DB table
        data = data.loc[:, ["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]]
        # Removing the ".BA" suffix from Argentinean tickers.
        data["Ticker"] = data["Ticker"].map(lambda x: x.replace(".BA", ""))
        # Converting the "Date" column to a timestamp integer for database compatibility.
        data["Date"] = data["Date"].map(lambda x: int(x.timestamp()))
        # Replacing nan values with -1 to find it easily in the database.
        float_cols = data.select_dtypes(include=["float"]).columns
        data[float_cols] = data[float_cols].fillna(-1.0)
        # Renaming columns to lowercase to match the database schema and converting the DataFrame to a list of dictionaries.
        data_dict = data.rename(columns=str.lower).to_dict(orient="records")
        logger.d(f"Downloaded data for tickers: {tickers} from {start_date} to {end_date}")
        if data_dict is None:
            logger.d(f"No data found for tickers: {tickers} from {start_date} to {end_date}")
            return []
        return data_dict

    def download_instruments_prices(self) -> list[dict]:
        """Return a list of available market tickers."""
        return []  # Not implemented for yfinance provider
