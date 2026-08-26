from typing import Any
from typing import Protocol
from ..common.app_logger import AppLogger
from ..repository.storage import Storage


logger = AppLogger.get_logger(__name__)


class BaseSystemStatsService(Protocol):
    def daily_bar_summary(self) -> dict[str, Any]:
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


class SystemStatsService(BaseSystemStatsService):
    """
    Service class for handling instrument-related operations.
    """

    def __init__(self,
                 storage: Storage):

        self.daily_bar_summary_view = storage.daily_bar_summary_view

    def daily_bar_summary(self) -> dict[str, Any]:

        try:
            return self.daily_bar_summary_view.query()[0]

        except Exception as ex:
            logger.ex(f"Error displaying daily bar summary: {ex}")
            raise
