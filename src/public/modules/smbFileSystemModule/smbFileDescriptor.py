from public import FileDescriptor
from typing import IO
import os

import smbclient

class SmbFileDescriptor(FileDescriptor):

    def __init__(self, fileFullPath: str, schemeAndLocation: str):
        self.fileFullPath = fileFullPath
        self.schemeAndLocation = schemeAndLocation
        self._cachedStat = None

    def open(self, mode='rb', buffering=-1, **kwargs) -> IO:
        return smbclient.open_file(self.fileFullPath, mode=mode, buffering=buffering, **kwargs)

    def _getFullPath(self) -> str:
        return self.fileFullPath

    def _getSchemeAndHost(self) -> str:
        return self.schemeAndLocation

    def _getStat(self) -> os.stat_result:
        if not self._cachedStat:
            self._cachedStat = smbclient.stat(self.fileFullPath)
        return self._cachedStat
