from unittest.mock import Mock

from jlatrading.repository.daily_bar_repo import DailyBarRepo


def test_init_stores_db_connection():
    db_conn = Mock()
    repo = DailyBarRepo(db_conn)

    assert repo.db_conn is db_conn


def test_save_returns_without_calling_db_for_empty_data():
    db_conn = Mock()
    repo = DailyBarRepo(db_conn)

    repo.save([])

    db_conn.insert_or_update.assert_not_called()


def test_save_calls_insert_or_update_with_expected_arguments():
    db_conn = Mock()
    repo = DailyBarRepo(db_conn)
    data = [
        {
            "ticker": "AAPL",
            "date": 20240101,
            "open": 100.0,
            "high": 110.0,
            "low": 95.0,
            "close": 108.0,
            "volume": 1000000,
        }
    ]

    repo.save(data)

    db_conn.insert_or_update.assert_called_once_with(
        "daily_bar_history",
        data,
        exclude_upd_cols=["ticker", "date"],
    )


def test_load_calls_query_table_with_default_projection():
    db_conn = Mock()
    db_conn.query_table.return_value = [{"ticker": "AAPL", "date": 20240101}]
    repo = DailyBarRepo(db_conn)

    result = repo.load({"ticker": "AAPL"})

    assert result == [{"ticker": "AAPL", "date": 20240101}]
    db_conn.query_table.assert_called_once_with(
        table="daily_bar_history",
        projection=[],
        filter={"ticker": "AAPL"},
        order_by=["ticker", "date"],
    )


def test_load_calls_query_table_with_custom_projection():
    db_conn = Mock()
    db_conn.query_table.return_value = [{"ticker": "AAPL"}]
    repo = DailyBarRepo(db_conn)

    result = repo.load({"ticker": "AAPL"}, fields=["ticker"])

    assert result == [{"ticker": "AAPL"}]
    db_conn.query_table.assert_called_once_with(
        table="daily_bar_history",
        projection=["ticker"],
        filter={"ticker": "AAPL"},
        order_by=["ticker", "date"],
    )
