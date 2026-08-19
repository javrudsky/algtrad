from .provider import MarketProvider


class CompoundProvider(MarketProvider):
    """
    A compound provider that combines the functionalities of IolProvider and YfinanceProvider.
    """
    def __init__(self,
                 iol_provider: MarketProvider,
                 yfinance_provider: MarketProvider):
        self.iol_provider = iol_provider
        self.yfinance_provider = yfinance_provider

    def download_instruments_prices(self) -> list[dict]:
        return self.iol_provider.download_instruments_prices()

    def download_daily_bar(self, tickers: list[str], start_date: str, end_date: str) -> str:
        return self.yfinance_provider.download_daily_bar(tickers, start_date, end_date)
