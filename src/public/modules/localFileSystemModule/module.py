from public.fileSystemModule import FileSystemModule
from public.fileDescriptor import FileDescriptor

from .localFileDescriptor import LocalFileDescriptor

import os
from urllib.parse import ParseResult
from typing import Iterable, List, IO
import itertools

import sqlalchemy

class LocalFileSystemModule(FileSystemModule):

    def __init__(self, relativePath = None):
        self.basePath = None
        self.relativePath = relativePath
    
    @staticmethod
    def handledURLSchemes() -> str or List[str] or Iterable[str]:
        return [ 'file' ]

    def connect(self, parsedUri: ParseResult, config: dict) -> None:
        self.basePath = parsedUri.path
        

    def listFiles(self) -> Iterable[FileDescriptor]:
        
        if not self.basePath:
            raise RuntimeError('LocalFileSystemModule not connected. You should connect to the data source before listing files.')

        searchPath = self.basePath
        if not os.path.isabs(searchPath):
            if not self.relativePath:
                raise RuntimeError('Expect to list files using a relative path but relative location not given')
            searchPath = os.path.join(searchPath, self.relativePath)

        return itertools.chain.from_iterable(map(lambda filename: LocalFileDescriptor(os.path.join(dirpath, filename)), filenames) for dirpath, dirnames, filenames in os.walk(searchPath))