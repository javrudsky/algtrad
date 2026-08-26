from typing import Any
from .view import DbView


class DailyBarSummaryView(DbView):
    """
    Repository for storing and retrieving symbol historical data.
    """

    SUMMARY_VIEW_NAME = "daily_bar_summary_v"

    def __init__(self, db_conn):
        """
        Initialize the DailyBarRepository.
        """
        # Initialization code for the repository goes here
        self.db_conn = db_conn

    def query(self, filter: dict[str, Any] | None = None, fields: list[str] | None = None) -> list[dict[str, Any]]:
        """
        Load daily bar rows from the repository using equality filters.
        """
        return self.db_conn.query_table(table=self.SUMMARY_VIEW_NAME,
                                        projection=fields or [],
                                        filter=filter or {},
                                        order_by=[])
