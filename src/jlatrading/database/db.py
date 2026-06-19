from abc import ABC


class Db(ABC):
    """
    Abstract base class for databases.
    """

    def is_connected(self) -> bool:
        """
        Check if the database connection is currently open.
        """
        return False

    def connect(self):
        """
        Connect to the database.
        """
        pass

    def disconnect(self):
        """
        Disconnect from the database.
        """
        pass

    def execute_query(self, query: str) -> list[dict]:
        """
        Execute a query on the database.
        """
        ...

    def insert_or_update(self, table: str, data: list[dict], exclude_upd_cols: list[str] = []):
        """
        Insert data into the database.
        """
        pass

    def delete(self, table: str, filter: list[dict]):

        """
        Delete data from the database.
        """
        pass
