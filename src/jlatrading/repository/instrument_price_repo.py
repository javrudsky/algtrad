from .repo_helper import RepoHelper
from .repository import Repository
from typing import Any, Mapping, Sequence


class InstrumentPriceRepo(Repository):
    """
    Repository for storing and retrieving instrument price snapshots.
    """

    TABLE_NAME = "instruments_prices"

    def __init__(self, db_conn):
        """
        Initialize the repository with a database connection.
        """
        self.db_conn = db_conn

    def save(self, data: Sequence[Mapping[str, Any]]) -> None:
        """
        Save instrument price rows into the repository.

        Rows are upserted using the unique key
        (symbol, timestamp, settlement_term).
        """
        if not data:
            return

        rows = [dict(row) for row in data]
        self.db_conn.insert_or_update(
            self.TABLE_NAME,
            rows,
            exclude_upd_cols=["symbol", "timestamp", "settlement_term"],
        )

    def load(
        self,
        filter: dict[str, Any],
        fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Load instrument price rows from the repository using equality filters.
        """
        return self.db_conn.query_table(table=self.TABLE_NAME,
                                        projection=fields or "*",
                                        filter=filter,
                                        order_by=["symbol", "timestamp", "settlement_term"])
