from abc import ABC, abstractmethod
from urllib.parse import ParseResult
import datetime
import os
import logging
from typing import IO

import public.magicTools as magicTools
import magic

logger = logging.getLogger('fileIndexer').getChild('public.FileDescriptor')

class FileDescriptor(ABC):

    @abstractmethod
    def getStat(self) -> os.stat_result:
        pass

    @abstractmethod
    def open(self, mode='rb', buffering=-1) -> IO:
        pass

    @abstractmethod
    def getFileFullPath(self) -> str:
        pass

    def getFileName(self) -> str:
        return os.path.basename(self.getFileFullPath())

    def getFilePath(self) -> str:
        return os.path.dirname(self.getFileFullPath())

    def getFileSizeKB(self) -> int:
        return int(self.getStat().st_size / 1024)

    def getCreationDateTime(self):
        return datetime.datetime.fromtimestamp(self.getStat().st_ctime)

    def getModificationDateTime(self):
        return datetime.datetime.fromtimestamp(self.getStat().st_mtime)

    def getFileMagic(self, ms_flags=magicTools.MAGIC_FLAGS_DEFAULT):

        with self.open(mode='rb') as buffer:
            buffer = buffer.read(1024)
            ms = magicTools.getMagic(ms_flags)
            magic = ms.buffer(buffer)
            if not magic:
                logger.debug('Unable to get magic info (%s)' % ms.error())
                buffer += buffer.read(-1)

            if not magic:
                logger.error('Unable to get magic info (%s)' % ms.error())
                return '__UNKNOWN__'

            return magic


    def getFileMime(self):
        return self.getFileMagic(ms_flags=magic.MIME_TYPE)

    def getFileEncoding(self):
        return self.getFileMagic(ms_flags=magic.MIME_ENCODING)

    def getFileDescription(self):
        return self.getFileMagic(ms_flags=magic.NONE)