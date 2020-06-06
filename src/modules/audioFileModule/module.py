from typing import Iterable, Dict

from public import FileHandleModule, ConfigHandler, FileDescriptor

import sqlalchemy

import mutagen


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


    def handle(self, fileDescriptor: FileDescriptor, dbEngine: sqlalchemy.engine.Engine, haveBeenModified: bool) -> None:
        
        with fileDescriptor.open() as _file:
            mutagenFile = mutagen.File(_file)
            try:
                pass
                # print(mutagenFile)
                # print(mutagenFile.info)
                # print(mutagenFile.tags)
            except Exception as ex:
                print('Got exception [%s]' % repr(ex))
                print('Error with file [%s]' % fileDescriptor.fullPath)
        pass