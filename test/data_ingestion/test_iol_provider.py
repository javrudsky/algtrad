from unittest.mock import MagicMock, Mock, call, patch

from jlatrading.data_ingestion.iol_provider import IolProvider


def _make_future(result=None, exc=None):
    future = MagicMock()
    if exc is not None:
        future.result.side_effect = exc
    else:
        future.result.return_value = result
    return future


def test_init_stores_iol_client():
    iol_client = Mock()

    provider = IolProvider(iol_client)

    assert provider.iol_client is iol_client


@patch("jlatrading.data_ingestion.iol_provider.as_completed")
@patch("jlatrading.data_ingestion.iol_provider.ThreadPoolExecutor")
def test_download_instruments_prices_aggregates_results(
    mock_executor_cls,
    mock_as_completed,
):
    iol_client = Mock()
    provider = IolProvider(iol_client)

    instrument_types = ["acciones", "cedears", "bonos"]
    futures = [
        _make_future({"titulos": [{"simbolo": "AAL"}]}),
        _make_future({"titulos": [{"simbolo": "GGAL"}, {"simbolo": "PAMP"}]}),
        _make_future({"titulos": []}),
    ]

    executor = MagicMock()
    executor.__enter__.return_value = executor
    executor.__exit__.return_value = None
    executor.submit.side_effect = futures
    mock_executor_cls.return_value = executor
    mock_as_completed.side_effect = lambda future_to_value: list(future_to_value.keys())

    with patch.object(IolProvider, "INSTRUMENT_TYPES", instrument_types):
        result = provider.download_instruments_prices()

    symbols_result = [{"symbol": inst["symbol"]} for inst in result]

    print(symbols_result)
    assert symbols_result == [
        {"symbol": "AAL"},
        {"symbol": "GGAL"},
        {"symbol": "PAMP"},
    ]
    mock_executor_cls.assert_called_once_with(max_workers=3)
    assert executor.submit.call_args_list == [
        call(iol_client.get_prices_by_instrument_type, "acciones"),
        call(iol_client.get_prices_by_instrument_type, "cedears"),
        call(iol_client.get_prices_by_instrument_type, "bonos"),
    ]


@patch("jlatrading.data_ingestion.iol_provider.as_completed")
@patch("jlatrading.data_ingestion.iol_provider.ThreadPoolExecutor")
def test_download_instruments_prices_logs_errors_and_continues(
    mock_executor_cls,
    mock_as_completed,
):
    iol_client = Mock()
    provider = IolProvider(iol_client)

    instrument_types = ["acciones", "cedears"]
    future_ok = _make_future({"titulos": [{"simbolo": "AAL"}]})
    future_error = _make_future(exc=RuntimeError("boom"))

    executor = MagicMock()
    executor.__enter__.return_value = executor
    executor.__exit__.return_value = None
    executor.submit.side_effect = [future_ok, future_error]
    mock_executor_cls.return_value = executor
    mock_as_completed.side_effect = lambda future_to_value: list(future_to_value.keys())

    with patch.object(IolProvider, "INSTRUMENT_TYPES", instrument_types):
        result = provider.download_instruments_prices()

    symbols_result = [{"symbol": inst["symbol"]} for inst in result]
    assert symbols_result == [{"symbol": "AAL"}]


def test_download_daily_bar_returns_empty_json_array():
    provider = IolProvider(Mock())

    result = provider.download_daily_bar(
        tickers=["AAL", "GGAL"],
        start_date="2026-01-01",
        end_date="2026-01-31",
    )

    assert result == "[]"
