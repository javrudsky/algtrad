
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
        selected_fields = fields or [
            "id",
            "ticker",
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        quoted_fields = ", ".join(f'"{field}"' for field in selected_fields)

        query = f"""
            SELECT {quoted_fields}
            FROM {self.TABLE_NAME}
        """

        if filter:
            where_clause = " AND ".join(
                f'"{column}" = {RepoHelper.sql_literal(value)}'
                for column, value in filter.items()
            )
            query += f"\nWHERE {where_clause}"

        query += "\nORDER BY ticker, date"
        return self.db_conn.execute_query(query)
