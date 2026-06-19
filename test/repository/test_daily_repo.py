
from jlatrading.database.db import Db
from jlatrading.repository.daily_bar_repo import DailyBarRepo

from jlatrading.common.app_logger import AppLogger

"""
Using an inmemory database to test the DailyBarRepo class for now.
It seems easely testable without needing to mock the database connection, and it allows us to test the actual SQL queries being executed.
"""
logger = AppLogger.get_logger(__name__)


def test_save_inserts_rows(db) -> None:
    repo = DailyBarRepo(db)

    repo.save(
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

    rows = db.execute_query(
        """
        SELECT ticker, date, open, high, low, close, volume
        FROM daily_bar_history
        ORDER BY ticker, date
        """
    )

    assert len(rows) == 2
    assert rows[0]["ticker"] == "AAPL"
    assert str(rows[0]["date"]) == "2024-01-01"
    assert rows[0]["close"] == 105.0
    assert rows[1]["ticker"] == "MSFT"
    assert str(rows[1]["date"]) == "2024-01-02"
    assert rows[1]["volume"] == 2000


def test_save_updates_existing_row(db: Db) -> None:
    repo = DailyBarRepo(db)

    repo.save(
        [
            {
                "ticker": "AAPL",
                "date": "2024-01-01",
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000,
            }
        ]
    )
    repo.save(
        [
            {
                "ticker": "AAPL",
                "date": "2024-01-01",
                "open": 101.0,
                "high": 111.0,
                "low": 96.0,
                "close": 106.0,
                "volume": 2000,
            }
        ]
    )

    rows = repo.load({"ticker": "AAPL", "date": "2024-01-01"})

    assert rows == [
        {
            "id": 1,
            "ticker": "AAPL",
            "date": rows[0]["date"],
            "open": 101.0,
            "high": 111.0,
            "low": 96.0,
            "close": 106.0,
            "volume": 2000,
        }
    ]
    assert str(rows[0]["date"]) == "2024-01-01"


def test_save_ignores_empty_data(db: Db) -> None:
    repo = DailyBarRepo(db)

    repo.save([])

    rows = db.execute_query("SELECT id FROM daily_bar_history")
    assert rows == []


def test_load_returns_all_fields_by_default(db: Db) -> None:
    repo = DailyBarRepo(db)
    repo.save(
        [
            {
                "ticker": "AAPL",
                "date": "2024-01-01",
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000,
            }
        ]
    )

    rows = repo.load({"ticker": "AAPL"})

    assert len(rows) == 1
    assert set(rows[0].keys()) == {
        "id",
        "ticker",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
    }


def test_load_returns_only_requested_fields(db: Db) -> None:
    repo = DailyBarRepo(db)
    repo.save(
        [
            {
                "ticker": "AAPL",
                "date": "2024-01-01",
                "open": 100.0,
                "high": 110.0,
                "low": 95.0,
                "close": 105.0,
                "volume": 1000,
            }
        ]
    )

    rows = repo.load({"ticker": "AAPL"}, fields=["ticker", "close"])

    assert rows == [{"ticker": "AAPL", "close": 105.0}]
