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
        file_mime = fileDescriptor.getFileMime()
        return not any(map(lambda m: file_mime == m, noTagMimes))


    def handle(self, fileDescriptor: FileDescriptor, dbEngine: sqlalchemy.engine.Engine, haveBeenModified: bool) -> None:
        '''
            Perform data extraction from the given file.

            :param fileDescriptor: A file descriptor, used by the module to acquire informations.
            :type fileDescriptor: :class:`public.fileDescriptor.FileDescriptor`
            :param dbEngine: A SQLAlchemy engine to query the configured database.
            :type dbEngine: :class:`sqlalchemy.engine.Engine`
            :param haveBeenModifier: Inform whether this file have been modified since last execution.
                                        This information should be used in order to avoid useless processing.
            :type haveBeenModified: bool
        '''
        with fileDescriptor.open() as _file:
            mutagenFile = mutagen.File(_file)
            try:
                print(mutagenFile)
                print(mutagenFile.info)
                print(mutagenFile.tags)
            except Exception as ex:
                print('Got exception [%s]' % repr(ex))
                print('Error with file [%s]' % fileDescriptor.getFileFullPath())
        pass