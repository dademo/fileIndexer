from typing import Iterable, Dict

from public import FileHandleModule, ConfigHandler, FileDescriptor

import sqlalchemy


class VideoFileModule(FileHandleModule):


    @staticmethod
    def handledFileMimes() -> str or Iterable[str]:
        return 'video/*'

    def requiredModules(self) -> Iterable[str] or None:
        return [
            'CoreModule'
        ]

    # Database
    def getDatabaseSchema(self) -> str:
        return 'video'

    def defineTables(self, metadata: sqlalchemy.MetaData, configuration: ConfigHandler) -> None:
        self.tables = {}

    def getSharedTables(self) -> Dict[str, sqlalchemy.Table]:
        return self.tables.copy()

    # Processing
    def canHandle(self, fileDescriptor: FileDescriptor) -> bool:
        # Can basicly handle any type of audio file
        return True


    def handle(self, fileDescriptor: FileDescriptor, dbEngine: sqlalchemy.engine.Engine, appConfig: ConfigHandler) -> None:
        '''
            Perform data extraction from the given file.

            :param fileDescriptor: A file descriptor, used by the module to acquire informations.
            :type fileDescriptor: :class:`public.fileDescriptor.FileDescriptor`
            :param dbEngine: A SQLAlchemy engine to query the configured database.
            :type dbEngine: :class:`sqlalchemy.engine.Engine`
        '''
        pass