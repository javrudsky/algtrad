from unittest.mock import Mock

from jlatrading.repository.instrument_price_repo import InstrumentPriceRepo


def test_init_stores_db_connection():
    db_conn = Mock()
    repo = InstrumentPriceRepo(db_conn)

    assert repo.db_conn is db_conn


def test_save_returns_without_calling_db_for_empty_data():
    db_conn = Mock()
    repo = InstrumentPriceRepo(db_conn)

    repo.save([])

    db_conn.insert_or_update.assert_not_called()


def test_save_calls_insert_or_update_with_expected_arguments():
    db_conn = Mock()
    repo = InstrumentPriceRepo(db_conn)
    data = [
        {
            "symbol": "AAL",
            "bid_quantity": 19,
            "bid_price": 12480.0,
            "ask_price": 12520.0,
            "ask_quantity": 5277,
            "last_price": 12500.0,
            "percent_change": -2.19,
            "open_price": 12640.0,
            "high_price": 12660.0,
            "low_price": 12340.0,
            "previous_close": 12500.0,
            "volume": 6860,
            "operations_count": 95,
            "timestamp": "2026-07-14T11:36:56.31",
            "option_type": None,
            "strike_price": 0.0,
            "expiration_date": "",
            "market": "1",
            "currency": "1",
            "description": "Cedear American Airlines Group",
            "settlement_term": "T1",
            "minimum_lot_size": 1,
            "lot_size": 1,
        }
    ]

    repo.save(data)

    db_conn.insert_or_update.assert_called_once_with(
        "instruments_prices",
        data,
        exclude_upd_cols=["symbol", "timestamp", "settlement_term"],
    )


def test_load_calls_query_table_with_default_projection():
    db_conn = Mock()
    db_conn.query_table.return_value = [
        {"symbol": "AAL", "timestamp": "2026-07-14T11:36:56.31"}
    ]
    repo = InstrumentPriceRepo(db_conn)

    result = repo.load({"symbol": "AAL"})

    assert result == [{"symbol": "AAL", "timestamp": "2026-07-14T11:36:56.31"}]
    db_conn.query_table.assert_called_once_with(
        table="instruments_prices",
        projection="*",
        filter={"symbol": "AAL"},
        order_by=["symbol", "timestamp", "settlement_term"],
    )


def test_load_calls_query_table_with_custom_projection():
    db_conn = Mock()
    db_conn.query_table.return_value = [{"symbol": "AAL", "last_price": 12500.0}]
    repo = InstrumentPriceRepo(db_conn)

    result = repo.load({"symbol": "AAL"}, fields=["symbol", "last_price"])

    assert result == [{"symbol": "AAL", "last_price": 12500.0}]
    db_conn.query_table.assert_called_once_with(
        table="instruments_prices",
        projection=["symbol", "last_price"],
        filter={"symbol": "AAL"},
        order_by=["symbol", "timestamp", "settlement_term"],
    )
