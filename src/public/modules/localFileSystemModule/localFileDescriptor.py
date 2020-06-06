from public import FileDescriptor
from typing import IO

import os

class LocalFileDescriptor(FileDescriptor):

    def __init__(self, fileFullPath):
        self.fileFullPath = fileFullPath
        self._cachedStat = None

    def open(self, mode='rb', buffering=-1, **kwargs) -> IO:
        return open(self.fileFullPath, mode=mode, buffering=buffering, **kwargs)

    def _getFullPath(self) -> str:
        return os.path.abspath(self.fileFullPath)

    def _getSchemeAndHost(self) -> str:
        return 'file://'

    def _getStat(self) -> os.stat_result:
        if not self._cachedStat:
            self._cachedStat = os.stat(self.fileFullPath)
        return self._cachedStat
