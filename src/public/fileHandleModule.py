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
            :rtype: Iterable[str] or str
        '''
        pass

    @abstractmethod
    def requiredModules(self) -> Iterable[str] or None:
        '''
            List required modules. Their method :meth:`FileHandleModule.handle`
            will be called before this object.

            Returned values can be a class name (as given by ``__class__``) or
            a FQDN module class name.

            :returns: A list of required modules (abolute path or class name)
                        or ``None``.
            :rtype: Iterable[str]
        '''
        pass

    # Database
    @abstractmethod
    def getDatabaseSchema(self) -> str:
        '''
            Declares the database schema (used during the initialization to create
            all the required schemas).

            :returns: The name of the schema used by this module.
            :rtype: str
        '''
        pass

    @abstractmethod
    def defineTables(self, metadata: sqlalchemy.MetaData, configuration: ConfigHandler) -> None:
        '''
            Declares the tables used by this module using the given metadata.

            :param metadata: The metadata to configure (using the schema given
                                by :meth:`FileHandleModule.getDatabaseSchema`).
            :type metadata: :class:`sqlalchemy.schema.MetaData`
            :param configuration: The application configuration.
            :type configuration: :class:`public.configHandler.ConfigHandler`

            .. note::
                The declared tables should be saved in order to be retrieved
                with :meth:`FileHandleModule.getSharedtables`.
        '''
        pass

    @abstractmethod
    def getSharedTables(self) -> Dict[str, sqlalchemy.Table]:
        '''
            Return tables which can be used by other modules.

            :returns: Tables which can be used by other modules.
            :rtype: dict of [str, :class:`sqlalchemy.schema.Table`]
        '''
        pass

    def getDBQuerier(self, dbEngine: sqlalchemy.engine.Engine, appConfig: ConfigHandler) -> object:
        '''
            Get an object which can query the database and return specific entities.

            Return ``None`` if not implemented.

            :return: an object which can query the database and return specific entities.
            :rtype: object
        '''
        return None

    # Processing
    @abstractmethod
    def canHandle(self, fileDescriptor: FileDescriptor) -> bool:
        '''
            Check whether this module can handle the given file (in addition to
            :meth:`FileHandleModule.handledFileMimes`).

            :param fileDescriptor: A file descriptor, used to check whether this
                                    module can handle this file.
            :type fileDescriptor: :class:`public.fileDescriptor.FileDescriptor`
            :returns: If this module can handle the given file.
            :rtype: bool
        '''
        pass

    @abstractmethod
    def handle(self, fileDescriptor: FileDescriptor, dbEngine: sqlalchemy.engine.Engine, appConfig: ConfigHandler) -> None:
        '''
            Perform data extraction from the given file.

            :param fileDescriptor: A file descriptor, used by the module to acquire
                                    informations.
            :type fileDescriptor: :class:`public.fileDescriptor.FileDescriptor`
            :param dbEngine: A SQLAlchemy engine to query the configured database.
            :type dbEngine: :class:`sqlalchemy.engine.Engine`
        '''
        pass