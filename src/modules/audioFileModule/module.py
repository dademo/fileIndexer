from typing import Iterable, Dict
import logging

from public import FileHandleModule, ConfigHandler, FileDescriptor

import sqlalchemy

import mutagen

logger = logging.getLogger('fileIndexer').getChild('modules.AudioFileModule')


class AudioFileModule(FileHandleModule):


    @staticmethod
    def handledFileMimes() -> str or Iterable[str]:
        return 'audio/*'

    def requiredModules(self) -> Iterable[str] or None:
        return [
            'CoreModule'
        ]

    # Database
    def getDatabaseSchema(self) -> str:
        return 'audio'

    def defineTables(self, metadata: sqlalchemy.MetaData, configuration: ConfigHandler) -> None:
        pass

    def getSharedTables(self) -> Dict[str, sqlalchemy.Table]:
        return {}

    # Processing
    def canHandle(self, fileDescriptor: FileDescriptor) -> bool:
        # Can basicly handle any type of audio file which have tags embedded
        noTagMimes = [
            'audio/x-wav'
        ]
        return not any(map(lambda m: fileDescriptor.mime == m, noTagMimes))


    def handle(self, fileDescriptor: FileDescriptor, dbEngine: sqlalchemy.engine.Engine, appConfig: ConfigHandler) -> None:
        
        with fileDescriptor.open() as _file:
            mutagenFile = mutagen.File(_file)
            try:
                pass
                # print(mutagenFile)
                # print(mutagenFile.info)
                # print(mutagenFile.tags)
            except Exception as ex:
                logger.error('Got exception [%s]' % repr(ex))
                logger.error('Error with file [%s]' % fileDescriptor.fullPath)
        pass