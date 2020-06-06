from typing import List, Iterable
from urllib.parse import ParseResult
from fnmatch import fnmatch
import logging

import smbclient

from public import FileSystemModule, FileDescriptor, ConfigHandler
from .config import configuration as moduleConfiguration
from .smbFileDescriptor import SmbFileDescriptor

logger = logging.getLogger('fileIndexer').getChild('public.modules.SmbFileSystemModule')


class SmbFileSystemModule(FileSystemModule):

    def __init__(self):
        self.schemeAndLocation = None

    @staticmethod
    def handledURLSchemes() -> str or List[str] or Iterable[str]:
        return [ 'smb' ]

    def connect(self, parsedUri: ParseResult, config: ConfigHandler) -> None:
        self.schemeAndLocation = '%s://%s' % (parsedUri.scheme, parsedUri.netloc)
        self.basePath = parsedUri.path
        smbclient.register_session(
            server=moduleConfiguration['server'],
            username=moduleConfiguration['username'],
            password=moduleConfiguration['password'],
            port=moduleConfiguration['port'],
            connection_timeout=moduleConfiguration['connection_timeout'])

    def listFiles(self,  ignorePatterns: List[str] = [], followSymlinks: bool=False) -> Iterable[FileDescriptor]:

        def list_dir_content(absoluteDirPath: str) -> Iterable[FileDescriptor]:
            for dirElement in smbclient.scandir(absoluteDirPath):
                if not any(map(lambda pattern: fnmatch(dirElement.path, pattern), ignorePatterns)):
                    if dirElement.is_file(follow_symlinks=followSymlinks):
                        yield SmbFileDescriptor(dirElement.path, self.schemeAndLocation)
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

        return list_dir_content(searchPath)