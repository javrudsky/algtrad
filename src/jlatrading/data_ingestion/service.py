from typing import Protocol
import json
from .provider import MarketProvider
from ..repository.repository import Repository
from ..common.app_logger import AppLogger

logger = AppLogger.get_logger(__name__)


class BaseMarketService(Protocol):
    def download_daily_bar(self, tickers: list[str], start_date: str, end_date: str) -> int:
        """
        Get historical price data for the specified tickers and date range.
        Args:
            tickers: List of market tickers or tickers to query.
            start_date: Start date in "YYYY-MM-DD" format.
            end_date: End date in "YYYY-MM-DD" format.
        Returns:
            A list of integers representing the historical price data for the specified tickers and date range.
        """
        ...


class MarketService(BaseMarketService):
    """
    Service class for handling instrument-related operations.
    """

    def __init__(self,
                 market_prov: MarketProvider,
                 daily_bar_repo: Repository):

        self.daily_bar_repo = daily_bar_repo
        self.market_prov = market_prov

    def download_daily_bar(self, tickers: list[str], start_date: str, end_date: str) -> int:
        # tickers = ["MELI.BA", "YPFD.BA"]
        records = -1
        try:
            json_hist = self.market_prov.download_daily_bar(tickers, start_date, end_date)

            print(f"Downloaded JSON data for tickers: {json_hist[:3]}...")
            dic_hist = json.loads(json_hist)

            print(f"Downloaded DIC data for tickers: {dic_hist[:3]}...")

            self.daily_bar_repo.save(dic_hist)
            records = len(dic_hist)
        except Exception as ex:
            logger.ex(f"Error downloading historical data for tickers: {tickers} from {start_date} to {end_date}: {ex}")
            raise
        logger.d(f"Downloaded and saved {records} records for tickers: {tickers} from {start_date} to {end_date}")
        return records
