from unittest.mock import Mock, patch
import importlib
import inspect

import pytest

from jlatrading.data_ingestion.service import MarketService


def test_download_daily_bar_returns_record_count_and_saves_data() -> None:
    provider = Mock()
    provider.download_daily_bar.return_value = [
        {
            "ticker": "AAPL",
            "date": "2024-01-01",
            "open": 100.0,
            "high": 110.0,
            "low": 95.0,
            "close": 105.0,
            "volume": 1000
        },
        {
            "ticker": "MSFT",
            "date": "2024-01-02",
            "open": 200.0,
            "high": 210.0,
            "low": 190.0,
            "close": 205.0,
            "volume": 2000
        }
    ]

    repo = Mock()
    storage = Mock()
    storage.daily_bar_repo = repo

    service = MarketService(provider, storage)

    result = service.download_daily_bar(
        ["AAPL", "MSFT"],
        "2024-01-01",
        "2024-01-31",
    )

    assert result == 2
    provider.download_daily_bar.assert_called_once_with(
        ["AAPL", "MSFT"],
        "2024-01-01",
        "2024-01-31",
    )
    repo.save.assert_called_once_with(
        [
            {
                "ticker": "AAPL",
                "date": "2024-01-01",
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000,
            },
            {
                "ticker": "MSFT",
                "date": "2024-01-02",
                "open": 200.0,
                "high": 210.0,
                "low": 190.0,
                "close": 205.0,
                "volume": 2000,
            },
        ]
    )


def test_download_daily_bar_returns_zero_for_empty_payload() -> None:
    provider = Mock()
    provider.download_daily_bar.return_value = []

    repo = Mock()
    storage = Mock()
    storage.daily_bar_repo = repo
    service = MarketService(provider, storage)

    result = service.download_daily_bar(
        ["AAPL"],
        "2024-01-01",
        "2024-01-31",
    )

    assert result == 0
    repo.save.assert_called_once_with([])


def test_download_daily_bar_reraises_provider_error() -> None:
    provider = Mock()
    provider.download_daily_bar.side_effect = RuntimeError("provider failed")
    repo = Mock()
    storage = Mock()
    storage.daily_bar_repo = repo
    service = MarketService(provider, storage)

    with pytest.raises(RuntimeError, match="provider failed"):
        service.download_daily_bar(
            ["AAPL"],
            "2024-01-01",
            "2024-01-31",
        )

    repo.save.assert_not_called()


def test_download_daily_bar_reraises_repository_error() -> None:
    provider = Mock()
    provider.download_daily_bar.return_value = [{"ticker": "AAPL", "date": "2024-01-01"}]
    repo = Mock()
    storage = Mock()
    storage.daily_bar_repo = repo
    repo.save.side_effect = RuntimeError("save failed")
    service = MarketService(provider, storage)

    with pytest.raises(RuntimeError, match="save failed"):
        service.download_daily_bar(
            ["AAPL"],
            "2024-01-01",
            "2024-01-31",
        )

    provider.download_daily_bar.assert_called_once_with(
        ["AAPL"],
        "2024-01-01",
        "2024-01-31",
    )


def test_download_instruments_prices_saves_downloaded_instruments_and_returns_count():
    provider = Mock()
    storage = Mock()
    storage.instrument_price_repo = Mock()
    service = MarketService(provider, storage)

    instruments = [{"symbol": "AAL"}, {"symbol": "GGAL"}]
    provider.download_instruments_prices.return_value = instruments

    result = service.download_instruments_prices()

    assert result == 2
    provider.download_instruments_prices.assert_called_once_with()
    storage.instrument_price_repo.save.assert_called_once_with(instruments)


def test_download_instruments_prices_logs_and_reraises_on_error():
    provider = Mock()
    storage = Mock()
    storage.instrument_price_repo = Mock()
    service = MarketService(provider, storage)

    provider.download_instruments_prices.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        service.download_instruments_prices()

    storage.instrument_price_repo.save.assert_not_called()
