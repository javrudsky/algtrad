from typer.testing import CliRunner
from unittest.mock import Mock

from jlatrading.cli import cli
from jlatrading.cli.cli import app
from jlatrading.common.utils import DateFormat


runner = CliRunner()


def build_daily_bar_h_params(tickers, start_date=None, end_date=None) -> list[str]:
    params = ["daily-bar-history"]
    for t in tickers:
        params.append(f"{t.strip()}")
    if start_date:
        params.append(f"--start-date={start_date}")
    if end_date:
        params.append(f"--end-date={end_date}")
    return params


def test_daily_bar_history_invokes_download_tickers(monkeypatch) -> None:
    p_tickers = ["MELI.BA", "YPFD.BA"]
    p_start_date = "2024-01-01"
    p_end_date = "2024-01-31"
    p_records = 10
    p_tickers_str = " ".join(f'{ticker.strip()}' for ticker in p_tickers)

    fake_srv = Mock()
    fake_srv.download_daily_bar.return_value = p_records

    monkeypatch.setattr(cli, "core", fake_srv)

    params = build_daily_bar_h_params(p_tickers, p_start_date, p_end_date)
    result = runner.invoke(
        app, params
    )

    assert result.exit_code == 0
    assert f"Getting data for period : {p_start_date} to {p_end_date}" in result.stdout
    assert f"Downloaded and saved {p_records} records for tickers: {p_tickers_str} from {p_start_date} to {p_end_date}"
    # fake_core.run.assert_called_once_with()

    fake_srv.download_daily_bar.assert_called_once_with(
            p_tickers,
            start_date=p_start_date,
            end_date=p_end_date,
            )


def test_daily_bar_history_uses_default_dates_when_missing(monkeypatch) -> None:

    # Arrange
    p_records = 10
    p_default_tickers = ["AAPL", "MSFT"]

    # Mocking the service to return a fixed number of records
    fake_srv = Mock()
    fake_srv.download_daily_bar.return_value = p_records
    monkeypatch.setattr(cli, "core", fake_srv)

    # Mocking the DateUtils to return a fixed date for today
    fake_du = Mock()
    first_date = "2024-02-01"
    today_date = "2024-02-15"
    fake_du.now_yyyymmdd_str.return_value = today_date
    fake_du.first_of_curr_month_yyyymmdd_str.return_value = first_date

    monkeypatch.setattr(cli, "du", fake_du)

    # Mocking the AppConfig to return a fixed list of default tickers
    fake_value = Mock()
    fake_value.to_strlist.return_value = p_default_tickers
    get_typed_value = Mock(return_value=fake_value)
    monkeypatch.setattr(cli.AppConfig, "get_typed_value", get_typed_value)

    # Act
    result = runner.invoke(app, ["daily-bar-history"])

    # Assert
    assert result.exit_code == 0

    assert "Missing tickers parameter, using default tickers from config: " + ", ".join(p_default_tickers)
    assert f"Using 1st of this month as start date since it was not provided: {first_date}" in result.stdout
    assert f"Using today as end date since it was not provided: {today_date}" in result.stdout
    assert f"Getting data for period : {first_date} to {today_date}" in result.stdout
    fake_srv.download_daily_bar.assert_called_once_with(
            p_default_tickers,
            start_date=first_date,
            end_date=today_date,
            )


def test_daily_bar_history_rejects_invalid_start_date() -> None:
    result = runner.invoke(app, ["daily-bar-history", "YPFD.BA", "--start-date=bad-date", "--end-date=2026-01-20"])

    assert result.exit_code != 0
    assert "Invalid start date format. Expected '2026-01-20'." in result.stdout


def test_daily_bar_history_rejects_invalid_end_date() -> None:
    result = runner.invoke(app, ["daily-bar-history", "YPFD.BA", "--start-date=2024-01-31", "--end-date=bad-date"])

    assert "Invalid end date format. Expected '2026-01-20'." in result.stdout


def test_daily_bar_history_bad_date_range() -> None:
    result = runner.invoke(app, ["daily-bar-history", "YPFD.BA", "--start-date=2024-01-31", "--end-date=2024-01-01"])

    assert "Start date must be less than or equal to end date." in result.stdout
