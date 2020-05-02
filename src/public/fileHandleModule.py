from .fileDescriptor import FileDescriptor

from abc import ABC, abstractmethod
from typing import Iterable, List, IO, Dict

import sqlalchemy


class FileHandleModule(ABC):
    
    @staticmethod
    @abstractmethod
    def handledFileMimes() -> str or List[str] or Iterable[str]:
        pass

    # Database
    @abstractmethod
    def getDatabaseSchema(self) -> str:
        pass

    @abstractmethod
    def defineTables(self, metadata: sqlalchemy.MetaData, configuration: dict) -> None:
        pass

    @abstractmethod
    def getSharedTables(self) -> Dict[str, sqlalchemy.Table]:
        pass

    # Processing
    @abstractmethod
    def canHandle(self, fileDescriptor: FileDescriptor, fileUri: str) -> bool:
        pass

    @abstractmethod
    def handle(self, fileDescriptor: FileDescriptor, dbConnection: sqlalchemy.engine.Engine, haveBeenModified: bool) -> dict:
        pass