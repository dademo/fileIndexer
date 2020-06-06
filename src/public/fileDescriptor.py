from abc import ABC, abstractmethod
from urllib.parse import ParseResult
import datetime
import os
import logging
from typing import IO
from functools import cached_property

import public.magicTools as magicTools
import magic

logger = logging.getLogger('fileIndexer').getChild('public.FileDescriptor')


class FileDescriptor(ABC):

    @cached_property
    def stat(self) -> os.stat_result:
        return self._getStat()
        
    @property
    def path(self):
        return self._getPath()

    @property
    def name(self):
        return self._getName()

    @property
    def fullPath(self):
        return self._getFullPath()

    @property
    def schemeAndHost(self):
        return self._getSchemeAndHost()

    @property
    def sizeKB(self):
        return self._getSizeKB()

    @property
    def creationDateTime(self):
        return self._getCreationDateTime()

    @property
    def modificationDateTime(self):
        return self._getModificationDateTime()


    @abstractmethod
    def _getStat(self) -> os.stat_result:
        pass

    @abstractmethod
    def open(self, mode='rb', buffering=-1, **kwargs) -> IO:
        pass

    def _getPath(self) -> str:
        return os.path.dirname(self.fullPath)

    def _getName(self) -> str:
        return os.path.basename(self.fullPath)

    @abstractmethod
    def _getFullPath(self) -> str:
        pass

    @abstractmethod
    def _getSchemeAndHost(self) -> str:
        pass

    def _getSizeKB(self) -> int:
        return int(self.stat.st_size / 1024)

    def _getCreationDateTime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.stat.st_ctime)

    def _getModificationDateTime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.stat.st_mtime)

    def _getFileMagic(self, ms_flags=magicTools.MAGIC_FLAGS_DEFAULT) -> str:

        try:
            magicTools.acquireLock()
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
        finally:
            magicTools.releaseLock()

    @cached_property
    def mime(self) -> str:
        return self._getFileMagic(ms_flags=magic.MIME_TYPE)

    @cached_property
    def encoding(self) -> str:
        return self._getFileMagic(ms_flags=magic.MIME_ENCODING)

    @cached_property
    def description(self) -> str:
        return self._getFileMagic(ms_flags=magic.NONE)