from abc import ABC, abstractmethod


class MarketProvider(ABC):

    @abstractmethod
    def download_daily_bar(self,
                           tickers: list[str],
                           start_date: str,
                           end_date: str) -> str:

        """Return daily historical price data for ``symbol`` between ``start`` and ``end``.
        Args:
            symbol: Market symbol or ticker to query.
            start: Start date in ``yyyy-mm-dd`` format.
            end: End date in ``yyyy-mm-dd`` format.
        Returns:
            A json string representing the historical price data for the specified symbol and date range.
        """
        pass
