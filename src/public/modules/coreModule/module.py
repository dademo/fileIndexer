from public.fileHandleModule import FileHandleModule, FileDescriptor
from public.configHandler import ConfigHandler
from typing import Iterable, List, IO, Dict
import logging
from .dbQuerier import DbQuerier

import sqlalchemy

logger = logging.getLogger('fileIndexer').getChild('public.modules.coreModule.CoreModule')


class CoreModule(FileHandleModule):

    def __init__(self):
        self.tables = {}

    @staticmethod
    def handledFileMimes():
        return '*'

    def requiredModules(self) -> Iterable[str] or None:
        return None

    def getDatabaseSchema(self) -> str:
        return 'core'
    
    def defineTables(self, metadata: sqlalchemy.MetaData, configuration: ConfigHandler) -> None:

        ##
        self.tables['file_mime'] = sqlalchemy.Table('file_mime', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, sqlalchemy.Sequence('file_mime_id_seq'), primary_key=True),
            sqlalchemy.Column('mime', sqlalchemy.String(255), index=True, unique=True, nullable=False)
        )
        self.tables['file_encoding'] = sqlalchemy.Table('file_encoding', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, sqlalchemy.Sequence('file_encoding_id_seq'), primary_key=True),
            sqlalchemy.Column('encoding', sqlalchemy.String(255), index=True, unique=True, nullable=False)
        )
        ##
        self.tables['file_path'] = sqlalchemy.Table('file_path', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, sqlalchemy.Sequence('file_path_id_seq'), primary_key=True),
            sqlalchemy.Column('path', sqlalchemy.String(4096), index=True, unique=True, nullable=False)
        )
        ##
        self.tables['file'] = sqlalchemy.Table('file', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, sqlalchemy.Sequence('file_id_seq'), primary_key=True),
            sqlalchemy.Column('id_file_mime', sqlalchemy.Integer, sqlalchemy.ForeignKey('file_mime.id', ondelete='CASCADE'), nullable=False),
            sqlalchemy.Column('id_file_encoding', sqlalchemy.Integer, sqlalchemy.ForeignKey('file_encoding.id', ondelete='CASCADE'), nullable=False),
            sqlalchemy.Column('id_file_path', sqlalchemy.Integer, sqlalchemy.ForeignKey('file_path.id', ondelete='CASCADE'), nullable=False),
            sqlalchemy.Column('filename', sqlalchemy.String(255), index=True, nullable=False),
            sqlalchemy.Column('size_kilobyte', sqlalchemy.Integer, nullable=False),
            sqlalchemy.Column('last_update', sqlalchemy.DateTime, index=True, default=None),    # Updated with sha
            sqlalchemy.Column('file_description', sqlalchemy.String),                      # Libmagic default output
            sqlalchemy.Column('hash', sqlalchemy.String(256), index=True, default=None)         # SHA-256
        )


    def getSharedTables(self) -> Dict[str, sqlalchemy.Table]:
        return self.tables.copy()

    def canHandle(self, fileDescriptor: FileDescriptor) -> bool:
        # Handle everything
        return True

    def handle(self, fileDescriptor: FileDescriptor, dbEngine: sqlalchemy.engine.Engine, haveBeenModified: bool) -> dict:
        dbQuerier = DbQuerier(dbEngine, self)
        if not dbQuerier.isFileInDatabase(fileDescriptor):
            #logger.info('File [%s] not in the database' % fileDescriptor.getFileFullName())
            dbQuerier.addFileInDatabase(fileDescriptor)