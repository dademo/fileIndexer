from public.fileSystemModule import FileSystemModule
from public.fileDescriptor import FileDescriptor
from public.configHandler import ConfigHandler
from public.configuration import moduleConfiguration

from .localFileDescriptor import LocalFileDescriptor

import os
import logging
from fnmatch import fnmatch
from urllib.parse import ParseResult
from typing import Iterable, List, IO
import itertools

import sqlalchemy


logger = logging.getLogger('fileIndexer').getChild(
    'public.modules.LocalFileSystemModule')


class LocalFileSystemModule(FileSystemModule):

    def __init__(self):
        self.basePath = None

    @staticmethod
    def handledURLSchemes() -> str or List[str] or Iterable[str]:
        return ['file']

    def connect(self, parsedUri: ParseResult, config: ConfigHandler) -> None:
        self.basePath = parsedUri.path
        self.config = config

    def listFiles(self, ignorePatterns: List[str] = [], followSymlinks: bool = False) -> Iterable[FileDescriptor]:

        def list_dir_content(absoluteDirPath: str) -> Iterable[FileDescriptor]:
            for dirElement in os.scandir(absoluteDirPath):
                if not any(map(lambda pattern: fnmatch(dirElement.path, pattern), ignorePatterns)):
                    if dirElement.is_file(follow_symlinks=followSymlinks):
                        yield LocalFileDescriptor(dirElement.path)
                    elif dirElement.is_dir(follow_symlinks=followSymlinks):
                        for subDirElement in list_dir_content(dirElement.path):
                            yield subDirElement
                    else:
                        # We can't handle this kind of file
                        logger.warn(
                            'Unable to process element [%s]' % dirElement.path)
                        pass

        if not self.basePath:
            raise RuntimeError(
                'LocalFileSystemModule not connected. You should connect to the data source before listing files.')

        searchPath = self.basePath
        if not os.path.isabs(searchPath):
            relativePath = self.config.get(moduleConfiguration['relativePath'])
            if not relativePath:
                raise RuntimeError(
                    'Expect to list files using a relative path but relative location not given')
            searchPath = os.path.join(searchPath, relativePath)

        return list_dir_content(searchPath)
