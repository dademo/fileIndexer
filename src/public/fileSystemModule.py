from public import FileDescriptor, ConfigHandler

from abc import ABC, abstractmethod
from typing import Iterable, List, IO
from urllib.parse import ParseResult

import sqlalchemy


class FileSystemModule(ABC):
    
    @staticmethod
    @abstractmethod
    def handledURLSchemes() -> str or List[str] or Iterable[str]:
        pass

    @abstractmethod
    def connect(self, parsedUri: ParseResult, config: ConfigHandler) -> None:
        pass

    @abstractmethod
    def listFiles(self,  ignorePatterns: List[str] = [], followSymlinks: bool=False) -> Iterable[FileDescriptor]:
        pass