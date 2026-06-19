from unittest.mock import Mock
import json
import pandas as pd

from jlatrading.data_ingestion.yfinance_provider import YFinanceProvider


def test_download_daily_bar_returns_empty_json_when_no_data() -> None:
    wrapper = Mock()
    wrapper.download.return_value = pd.DataFrame()
    provider = YFinanceProvider(wrapper)

    result = provider.download_daily_bar(
        ["AAPL", "MSFT"],
        "2024-01-01",
        "2024-01-31",
    )

    assert result == "[]"
    wrapper.download.assert_called_once_with(
            ["AAPL", "MSFT"],
            start="2024-01-01",
            end="2024-01-31",
            interval="1d",
        )


def test_download_daily_bar_returns_dataframe_as_json() -> None:
    data = pd.DataFrame(
        [
            {
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000,
            },
            {
                "open": 200.0,
                "high": 210.0,
                "low": 190.0,
                "close": 205.0,
                "volume": 2000,
            },
        ]
    )
    wrapper = Mock()
    wrapper.download.return_value = data
    provider = YFinanceProvider(wrapper)

    result = provider.download_daily_bar(
        ["AAPL"],
        "2024-01-01",
        "2024-01-02",
    )

    parsed = json.loads(result)

    assert parsed == [
        {
            "open": 100.0,
            "high": 110.0,
            "low": 95.0,
            "close": 105.0,
            "volume": 1000,
        },
        {
            "open": 200.0,
            "high": 210.0,
            "low": 190.0,
            "close": 205.0,
            "volume": 2000,
        },
    ]
    assert wrapper.calls == [
        {
            "tickers": ["AAPL"],
            "start": "2024-01-01",
            "end": "2024-01-02",
            "interval": "1d",
        }
    ]
