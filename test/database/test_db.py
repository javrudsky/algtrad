import pytest

from jlatrading.common.app_logger import AppLogger
from jlatrading.common.exceptions import DbError
from jlatrading.database.db import Db
from jlatrading.database.duck_db import DuckDb

logger = AppLogger.get_logger(__name__)


def test_connect_creates_database_parent_directory(tmp_path) -> None:
    logger.d(f"Test started - test_connect_creates_database_parent_directory: {tmp_path}")
    # Using tmp_path built in fixture
    db_path = tmp_path / "nested" / "market.duckdb"

    db = DuckDb(db_path)
    db.connect()

    try:
        assert db_path.parent.exists()
        assert db_path.parent.is_dir()
    finally:
        db.disconnect()


def test_connect_creates_configured_tables(db: Db) -> None:
    logger.d("Test started - test_connect_creates_configured_tables")
    rows = db.execute_query("SHOW TABLES")
    table_names = {row["name"] for row in rows}

    assert "daily_bar_history" in table_names


def test_execute_query_returns_rows_as_dicts(db: Db) -> None:
    logger.d("Test started - test_execute_query_returns_rows_as_dicts")
    rows = db.execute_query("SELECT 1 AS value, 'AAPL' AS ticker")

    assert rows == [{"value": 1, "ticker": "AAPL"}]


def test_execute_query_returns_empty_list_for_statements_without_result_set(db: Db) -> None:
    logger.d("Test started - test_execute_query_returns_empty_list_for_statements_without_result_set")
    rows = db.execute_query("CREATE TEMP TABLE temp_table(id INTEGER)")

    assert rows == []


def test_execute_query_raises_db_error_for_invalid_sql(db: Db) -> None:
    logger.d("Test started - test_execute_query_raises_db_error_for_invalid_sql")
    with pytest.raises(DbError, match="Failed executing query"):
        db.execute_query("SELECT FROM")


def test_insert_or_update_inserts_rows(db: Db) -> None:
    logger.d("Test started - test_insert_or_update_inserts_rows")
    db.insert_or_update(
        "daily_bar_history",
        [
            {
                "ticker": "AAPL",
                "date": 12345678,
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000,
            }
        ],
        exclude_upd_cols=["ticker", "date"],
    )

    rows = db.execute_query(
        """
        SELECT id, ticker, date, open, high, low, close, volume
        FROM daily_bar_history
        WHERE id = 1
        """
    )

    assert len(rows) == 1
    assert rows[0]["ticker"] == "AAPL"
    assert rows[0]["open"] == 100.0
    assert rows[0]["close"] == 105.0
    assert rows[0]["volume"] == 1000


def test_insert_or_update_updates_existing_rows(db: Db) -> None:
    logger.d("Test started - test_insert_or_update_updates_existing_rows")
    db.insert_or_update(
        "daily_bar_history",
        [
            {
                "ticker": "AAPL",
                "date": 12345678,
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000,
            }
        ],
        exclude_upd_cols=["ticker", "date"],
    )

    db.insert_or_update(
        "daily_bar_history",
        [
            {
                "ticker": "AAPL",
                "date": 12345678,
                "open": 101.0,
                "high": 111.0,
                "low": 96.0,
                "close": 106.0,
                "volume": 2000,
            }
        ],
        exclude_upd_cols=["ticker", "date"],
    )

    rows = db.execute_query(
        """
        SELECT id, ticker, open, high, low, close, volume
        FROM daily_bar_history
        WHERE ticker = 'AAPL' AND date = 12345678
        """
    )

    logger.d(f"Rows after update: {rows}")
    assert rows == [
        {
            "id": 1,
            "ticker": "AAPL",
            "open": 101.0,
            "high": 111.0,
            "low": 96.0,
            "close": 106.0,
            "volume": 2000,
        }
    ]


def test_insert_or_update_rejects_rows_with_different_keys(db: Db) -> None:
    with pytest.raises(ValueError, match="All rows must contain the same keys."):
        db.insert_or_update(
            "daily_bar_history",
            [
                {
                    "ticker": "AAPL",
                    "date": 12345678,
                    "open": 100.0,
                    "high": 110.0,
                    "low": 95.0,
                    "close": 105.0,
                    "volume": 1000,
                },
                {
                    "ticker": "MSFT",
                },
            ],
            exclude_upd_cols=["ticker", "date"],
        )


def test_delete_removes_rows_matching_all_filters(db: Db) -> None:
    logger.d("Test started - test_delete_removes_rows_matching_all_filters")
    db.insert_or_update(
        "daily_bar_history",
        [
            {
                "ticker": "AAPL",
                "date": 12345678,
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000,
             },
            {
                "ticker": "MSFT",
                "date": 12345679,
                "open": 200.0,
                "high": 210.0,
                "low": 190.0,
                "close": 205.0,
                "volume": 2000,
            },
        ],
        exclude_upd_cols=["ticker", "date"],
    )

    db.delete("daily_bar_history", [{"id": 1}, {"ticker": "MSFT", "date": 12345679}])

    rows = db.execute_query("SELECT id, ticker FROM daily_bar_history ORDER BY id")

    assert rows == []


def test_delete_rejects_empty_filter(db: Db) -> None:
    with pytest.raises(ValueError, match="At least one filter must be provided for delete."):
        db.delete("daily_bar_history", [])


def test_delete_rejects_empty_filter_entry(db: Db) -> None:
    with pytest.raises(ValueError, match="Filter entries must not be empty."):
        db.delete("daily_bar_history", [{}])
