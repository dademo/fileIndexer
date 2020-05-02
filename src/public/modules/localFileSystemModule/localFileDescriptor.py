from public import FileDescriptor
from typing import IO

import os

class LocalFileDescriptor(FileDescriptor):

    def __init__(self, fileFullPath):
        self.fileFullPath = fileFullPath

    def open(self, mode='rb', buffering=-1) -> IO:
        return open(self.fileFullPath, mode=mode, buffering=buffering)

    def getFileFullPath(self) -> str:
        return os.path.abspath(self.fileFullPath)

    def getStat(self) -> os.stat_result:
        return os.stat(self.getFileFullPath())
