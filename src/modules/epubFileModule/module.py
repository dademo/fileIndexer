from typing import Iterable, Dict

from public import FileHandleModule, ConfigHandler, FileDescriptor

import sqlalchemy


class EpubFileModule(FileHandleModule):


    @staticmethod
    def handledFileMimes() -> str or Iterable[str]:
        return 'application/epub*'

    def requiredModules(self) -> Iterable[str] or None:
        return [
            'CoreModule'
        ]

    # Database
    def getDatabaseSchema(self) -> str:
        return 'epub'

    def defineTables(self, metadata: sqlalchemy.MetaData, configuration: ConfigHandler) -> None:
        pass

    def getSharedTables(self) -> Dict[str, sqlalchemy.Table]:
        return {}

    # Processing
    def canHandle(self, fileDescriptor: FileDescriptor) -> bool:
        # Can basicly handle any type of audio file
        return True


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
        pass