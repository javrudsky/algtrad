from datetime import datetime
from unittest.mock import Mock
import pandas as pd

from jlatrading.data_ingestion.yfinance_provider import YFinanceProvider

d1 = datetime(2024, 1, 1)
d2 = datetime(2024, 1, 2)


def mock_yfinance_data() -> pd.DataFrame:

    dfy = pd.DataFrame({
        # "Date": ["2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02"],
        "Date": [d1, d2, d1, d2],
        "Ticker": ["YPF", "YPF", "AAL", "AAL"],
        "Close": [15, 25, 35, 45],
        "High": [12, 22, 32, 42],
        "Low": [8, 18, 28, 38],
        "Open": [10, 20, 30, 40],
        "Volume": [100, 200, 300, 400],
        }
                        )
    dfy = dfy.pivot(index="Date", columns="Ticker", values=["Close", "High", "Low", "Open", "Volume"])
    dfy.columns.names = ["Price", "Ticker"]
    return dfy


def mock_yfinance_processed() -> pd.DataFrame:
    data = mock_yfinance_data()
    data = (
            data.stack(level="Ticker")
            .reset_index()
            # .rename(columns={"level_1": "Ticker"})
            )

    return data


def mock_yfinance_dict() -> list[dict]:
    df = mock_yfinance_processed()
    df = df.rename(columns=str.lower)
    df["date"] = df["date"].map(lambda x: 1704067200 if x == d1 else 1704153600)
    dict_data = df.to_dict(orient="records")
    if dict_data is None:
        return []
    return dict_data


def test_download_daily_bar_returns_empty_dict_when_no_data() -> None:
    wrapper = Mock()
    wrapper.download.return_value = pd.DataFrame()
    provider = YFinanceProvider(wrapper)

    result = provider.download_daily_bar(
            ["YPF", "AAL"],
            "2024-01-01", "2024-01-31"
            )

    assert result == []

    # Yfinance library needs the ".BA" suffix for Argentinian tickers.
    wrapper.download.assert_called_once_with(
            ["YPF.BA", "AAL.BA"],
            start="2024-01-01",
            end="2024-01-31",
            interval="1d",
        )


def test_download_daily_bar_returns_dataframe_as_dict() -> None:
    data = pd.DataFrame(mock_yfinance_data())
    wrapper = Mock()
    wrapper.download.return_value = data
    provider = YFinanceProvider(wrapper)

    result = provider.download_daily_bar(
        ["YPF", "AAL"],
        "2024-01-01",
        "2024-01-02",
    )
    mocked = mock_yfinance_dict()
    mocked = sorted(mocked, key=lambda d: (d["ticker"], d["date"]))
    result = sorted(result, key=lambda d: (d["ticker"], d["date"]))

    assert result == mocked
    # Yfinance library needs the ".BA" suffix for Argentinian tickers.
    wrapper.download.assert_called_once_with(
            ["YPF.BA", "AAL.BA"],
            start="2024-01-01",
            end="2024-01-02",
            interval="1d",
        )
