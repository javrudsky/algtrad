from typing import Any


class RepoHelper:
    """
    Helper class for repository operations.
    """

    @staticmethod
    def sql_literal(value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if isinstance(value, (int, float)):
            return str(value)

        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"
