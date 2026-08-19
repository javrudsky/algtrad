
from typing import Any, Mapping, Sequence
from .repository import Repository
from .repo_helper import RepoHelper


class DailyBarRepo(Repository):
    """
    Repository for storing and retrieving symbol historical data.
    """

    TABLE_NAME = "daily_bar_history"

    def __init__(self, db_conn):
        """
        Initialize the DailyBarRepository.
        """
        # Initialization code for the repository goes here
        self.db_conn = db_conn

    def save(self, data: Sequence[Mapping[str, Any]]) -> None:
        """
        Save daily bar rows into the repository.

        Rows are upserted using the unique key (ticker, date).
        """
        if not data:
            return

        rows = [dict(row) for row in data]
        self.db_conn.insert_or_update(
            "daily_bar_history",
            rows,
            exclude_upd_cols=["ticker", "date"],
        )

    def load(self, filter: dict[str, Any], fields: list[str] | None = None) -> list[dict[str, Any]]:
        """
        Load daily bar rows from the repository using equality filters.
        """
        return self.db_conn.query_table(table=self.TABLE_NAME,
                                        projection=fields or [],
                                        filter=filter,
                                        order_by=["ticker", "date"])
