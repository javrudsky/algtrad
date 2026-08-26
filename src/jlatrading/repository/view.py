from typing import Any
from abc import ABC, abstractmethod


class DbView(ABC):
    """
    Abstract base class for database views.
    """

    @abstractmethod
    def query(self, filter: dict[str, Any] | None = None, fields: list[str] | None = None) -> list[dict[str, Any]]:
        """
        Load data from the database view.
        """
        pass
