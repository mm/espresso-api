"""Module for importing backups and bookmarks from other services.
"""

import abc
from typing import List, Optional
from collections import namedtuple
from src.model import Link

ImportStats = namedtuple('ImportStats', ['imported', 'errors'])

class BaseImporter(metaclass=abc.ABCMeta):
    """Interface for defining certain kinds of importers. All
    importers should implement all abstract methods here.
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            (hasattr(subclass, 'extract_links') and callable(subclass.load_links))
            and (hasattr(subclass, 'transform_links') and callable(subclass.transform_links))
            and (hasattr(subclass, 'load_links') and callable(subclass.load_links))
            or NotImplemented
        )

    @abc.abstractmethod
    def extract_links(self, path:str) -> List[Optional[dict]]:
        """Extracts links from data to be imported, and returns a list
        of dict objects.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def transform_links(self, links: List[dict], **kwargs) -> List[Link]:
        """Transforms a set of links after being extracted from source.
        Any data manipulation happens in this step.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def load_links(self, links: List[Link]) -> ImportStats:
        """Loads a list of links into the database, and returns statistics
        on how many were imported vs. how many had errors.
        """
        raise NotImplementedError