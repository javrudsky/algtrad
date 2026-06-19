from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence


class Repository(ABC):
    """
    Abstract base class for repositories.
    """

    @abstractmethod
    def save(self, data: Sequence[Mapping[str, Any]]) -> None:
        """
        Save data to the repository.
        """
        pass

    @abstractmethod
    def load(self, filter: dict[str, Any], fields: list[str] | None = None) -> list[dict[str, Any]]:
        """
        Load data from the repository using an identifier.
        """
        pass
