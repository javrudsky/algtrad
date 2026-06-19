import duckdb
from pathlib import Path

from .db import Db
from .db_tables import tables_config
from ..common.exceptions import DbError
from ..common.app_logger import AppLogger

logger = AppLogger.get_logger(__name__)


class DuckDb(Db):
    def __init__(self, db_path: str | None = None):
        self.conn = None
        self.db_path = db_path

    def __open_connection(self) -> duckdb.DuckDBPyConnection:
        """
        Create and return a DuckDB connection to the application database.

            Ensures the parent directory of the database file exists before opening
            the connection.

            Returns:
                An open DuckDB connection bound to the configured database path.
        """
        db_path = self.db_path
        logger.d(f"Opening DuckDB connection in {'memory' if db_path is None else db_path}")
        if db_path is None:
            logger.d("Using in-memory DuckDB instance.")
            return duckdb.connect()

        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(str(path))

    def is_connected(self) -> bool:
        """
        Check if the database connection is currently open.

        Returns:
            True if a connection is established, False otherwise.
        """
        return self.conn is not None

    def __checked_connection(self) -> duckdb.DuckDBPyConnection:
        """
        Ensure a database connection is established and return it.
        """
        if self.conn is None:
            logger.e("Database is not connected.")
            raise DbError("Database is not connected.")
        return self.conn

    def connect(self):
        """
        Initialize the database connection and create the configured schema.

        Opens a connection if one is not already available, then creates the
        sequences and tables defined in ``tables_config``.

        Raises:
            DbError: If the database structure cannot be created.
        """

        if self.conn is not None:
            logger.i(f"Database connection already established: {self.db_path}")
            return

        try:
            self.conn = self.__open_connection()
            logger.d("Creating database structure from configuration.")
            for table_config in tables_config:
                logger.d(f"Creating sequence and table for {table_config['table_name']}")
                self.conn.execute(f"CREATE SEQUENCE  IF NOT EXISTS { table_config['table_name'] }_id_seq START 1")
                self.conn.execute(table_config["insert_sql"])
        except duckdb.Error as exc:
            raise DbError(f"Failed creating database estructure: {str(exc)}") from exc

    def disconnect(self):
        """
        Close the database connection if it is open.
        """
        if self.conn is not None:
            logger.d("Closing database connection.")
            self.conn = None

    def execute_query(self, query: str) -> list[dict]:
        """
        Execute a SQL query and return the result set as a list of dictionaries.

        Args:
            query: SQL query to execute.

        Returns:
            Query results as a list of dictionaries. Returns an empty list for
            statements that do not produce a result set.

        Raises:
            DbError: If the query execution fails.
        """

        try:
            conn = self.__checked_connection()
            logger.d(f"Executing query: {query}")
            result = conn.execute(query)
        except duckdb.Error as exc:
            raise DbError(f"Failed executing query: {str(exc)}") from exc

        if result.description is None:
            return []

        columns = [column[0] for column in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]

    def insert_or_update(self, table: str, data: list[dict], exclude_upd_cols: list[str] = []):
        """
        Insert or update rows in the database.

        Assumes the target table has a PRIMARY KEY or UNIQUE constraint so
        ON CONFLICT can resolve duplicates.
        """
        if not data:
            return

        columns = list(data[0].keys())
        expected_keys = set(columns)

        for row in data:
            if set(row.keys()) != expected_keys:
                raise ValueError("All rows must contain the same keys.")

        quoted_table = f'"{table}"'
        quoted_columns = ", ".join(f'"{col}"' for col in columns)
        placeholders = ", ".join("?" for _ in columns)
        update_fields = ", ".join(f'"{col}"' for col in exclude_upd_cols)
        update_clause = ", ".join(
            f'"{col}" = EXCLUDED."{col}"' for col in columns if col not in exclude_upd_cols
        )

        rows = [
            tuple(row[col] for col in columns)
            for row in data
        ]

        sql = f"""
            INSERT INTO {quoted_table} ({quoted_columns})
            VALUES ({placeholders})
            ON CONFLICT ({update_fields}) DO UPDATE SET {update_clause}
        """
        logger.d(f"Executing insert_or_update with SQL: {sql} and data: {data}")
        try:
            conn = self.__checked_connection()
            conn.executemany(sql, rows)
        except duckdb.Error as exc:
            raise DbError(f"Failed inserting/updating data: {str(exc)}") from exc

    def delete(self, table: str, filter: list[dict]) -> None:
        """
        Delete rows from a DuckDB table matching the provided filters.

        Each dictionary in ``filter`` represents one predicate group. Keys are
        treated as column names and values as equality matches. Conditions
        inside one dictionary are combined with ``AND``, and multiple
        dictionaries are combined with ``OR``.

        Args:
            table: Name of the target table.
            filter: List of column-value mappings used to identify rows to delete.

        Raises:
            ValueError: If ``filter`` is empty or contains an empty condition.
            duckdb.Error: If DuckDB fails to execute the delete operation.
        """
        if not filter:
            raise ValueError("At least one filter must be provided for delete.")

        predicate_groups: list[str] = []
        values: list[object] = []

        for conditions in filter:
            if not conditions:
                raise ValueError("Filter entries must not be empty.")

            predicate = " AND ".join(f'"{column}" = ?' for column in conditions)
            predicate_groups.append(f"({predicate})")
            values.extend(conditions.values())

        quoted_table = f'"{table}"'
        where_clause = " OR ".join(predicate_groups)

        sql = f"""
            DELETE FROM {quoted_table}
            WHERE {where_clause}
        """

        try:
            conn = self.__checked_connection()
            conn.execute(sql, tuple(values))
        except duckdb.Error as exc:
            raise DbError(f"Failed deleting data: {str(exc)}") from exc
