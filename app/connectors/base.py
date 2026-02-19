
from abc import ABC, abstractmethod
from typing import Any, List


class BaseConnector(ABC):
    """
    Base interface for all data source connectors.
    """

    @abstractmethod
    def fetch(self, **kwargs: Any) -> List[Any]:
        """
        Fetch records from the underlying data source.
        """
        raise NotImplementedError

