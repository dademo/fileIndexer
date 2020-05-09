from public import FileDescriptor, ConfigHandler

from abc import ABC, abstractmethod
from typing import Iterable, Dict

import sqlalchemy


class FileHandleModule(ABC):
    
    @staticmethod
    @abstractmethod
    def handledFileMimes() -> str or Iterable[str]:
        '''
            Returns a list of handled file mimes. These values will be compared
            to the current file mime using :func:`fnmatch.fnmatch`.

            :returns: A list of handled file mimes or a single value.
        '''
        pass

    @abstractmethod
    def requiredModules(self) -> Iterable[str] or None:
        '''
            List required modules. Their method :meth:`FileHandleModule.handle` will
            be called before this object.

            :returns: A list of required modules (abolute path or class name) or ``None``.
        '''
        pass

    # Database
    @abstractmethod
    def getDatabaseSchema(self) -> str:
        '''
            Declares the database schema (used during the initialization to create all the
            required schemas).

            :returns: The name of the schema used by this module.
        '''
        pass

    @abstractmethod
    def defineTables(self, metadata: sqlalchemy.MetaData, configuration: ConfigHandler) -> None:
        '''
            Declares the tables used by this module using the given metadata.

            :param metadata: The metadata to configure (using the schema given by :meth:`FileHandleModule.getDatabaseSchema`).
            :param configuration: The application configuration.

            .. note::
                The declared tables should be saved in order to be retrieved with :meth:`FileHandleModule.getSharedtables`.
        '''
        pass

    @abstractmethod
    def getSharedTables(self) -> Dict[str, sqlalchemy.Table]:
        '''
            Return tables which can be used by other modules.

            :returns: Tables which can be used by other modules.
        '''
        pass

    # Processing
    @abstractmethod
    def canHandle(self, fileDescriptor: FileDescriptor) -> bool:
        '''
            Check whether this module can handle the given file (in addition to :meth:`FileHandleModule.handledFileMimes`).

            :param fileDescriptor: A file descriptor, used to check whether this module can handle this file.
            :returns: If this module can handle the given file.
        '''
        pass

    @abstractmethod
    def handle(self, fileDescriptor: FileDescriptor, dbConnection: sqlalchemy.engine.Engine, haveBeenModified: bool) -> None:
        '''
            Perform data extraction from the given file.

            :param fileDescriptor: A file descriptor, used by the module to acquire informations.
            :param dbConnection: A SQLAlchemy engine to query the configured database.
            :param haveBeenModifier: Inform whether this file have been modified since last execution.
                                        This information should be used in order to avoid useless processing.
        '''
        pass