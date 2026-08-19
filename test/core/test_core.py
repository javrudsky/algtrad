from unittest.mock import Mock, patch

import pytest

from jlatrading.common.utils import DateFormat
from jlatrading.core import core


def test_download_daily_bar_calls_market_service(monkeypatch) -> None:
    tickers = ["AAPL", "MSFT"]
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    expected_records = 2

    market_service = Mock()
    market_service.download_daily_bar.return_value = expected_records
    build_market_service = Mock(return_value=market_service)

    monkeypatch.setattr(core.cf, "build_market_service", build_market_service)

    result = core.download_daily_bar(
        tickers,
        start_date=start_date,
        end_date=end_date,
    )

    assert result == expected_records
    build_market_service.assert_called_once_with()
    market_service.download_daily_bar.assert_called_once_with(
        tickers,
        start_date=start_date,
        end_date=end_date,
    )


def test_download_daily_bar_rejects_empty_tickers() -> None:
    tickers: list[str] = []
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    expected_message = "tickers must not be empty."

    with pytest.raises(ValueError, match=expected_message):
        core.download_daily_bar(tickers, start_date=start_date, end_date=end_date)


def test_download_daily_bar_rejects_blank_ticker() -> None:
    tickers = ["AAPL", "   "]
    start_date = "2024-01-01"
    end_date = "2024-01-31"
    expected_message = "All tickers must be non-empty strings."

    with pytest.raises(ValueError, match=expected_message):
        core.download_daily_bar(tickers, start_date=start_date, end_date=end_date)


def test_download_daily_bar_rejects_invalid_start_date() -> None:
    tickers = ["AAPL"]
    start_date = "bad-date"
    end_date = "2024-01-31"
    expected_message = f"Invalid start_date format. Expected {DateFormat.YYYYMMDD_FORMAT}."

    with pytest.raises(ValueError, match=expected_message):
        core.download_daily_bar(tickers, start_date=start_date, end_date=end_date)


def test_download_daily_bar_rejects_invalid_end_date() -> None:
    tickers = ["AAPL"]
    start_date = "2024-01-01"
    end_date = "bad-date"
    expected_message = f"Invalid end_date format. Expected {DateFormat.YYYYMMDD_FORMAT}."

    with pytest.raises(ValueError, match=expected_message):
        core.download_daily_bar(tickers, start_date=start_date, end_date=end_date)


def test_download_daily_bar_rejects_invalid_date_range() -> None:
    tickers = ["AAPL"]
    start_date = "2024-02-01"
    end_date = "2024-01-31"
    expected_message = "Start date must be less than or equal to end date."

    with pytest.raises(ValueError, match=expected_message):
        core.download_daily_bar(tickers, start_date=start_date, end_date=end_date)


@patch("jlatrading.core.core.cf.build_market_service")
def test_download_instruments_prices_builds_market_service_and_returns_result(
    mock_build_market_service,
):
    market_service = Mock()
    market_service.download_instruments_prices.return_value = 42
    mock_build_market_service.return_value = market_service

    result = core.download_instruments_prices()

    assert result == 42
    mock_build_market_service.assert_called_once_with()
    market_service.download_instruments_prices.assert_called_once_with()


@patch("jlatrading.core.core.cf.build_market_service")
def test_download_instruments_prices_propagates_service_errors(
    mock_build_market_service,
):
    market_service = Mock()
    market_service.download_instruments_prices.side_effect = RuntimeError("boom")
    mock_build_market_service.return_value = market_service

    with pytest.raises(RuntimeError, match="boom"):
        core.download_instruments_prices()

    mock_build_market_service.assert_called_once_with()
    market_service.download_instruments_prices.assert_called_once_with()
