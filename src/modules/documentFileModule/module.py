
from typing import Iterable, Dict
from fnmatch import fnmatch
import logging

from public import FileHandleModule, ConfigHandler, FileDescriptor

import sqlalchemy
from .processors import PdfProcessor, EpubProcessor
from .dbQuerier import DbQuerier

logger = logging.getLogger('fileIndexer').getChild('modules.DocumentFileModule')

# Processors
_processors = {
    'application/pdf': PdfProcessor(),
    'application/epub*': EpubProcessor(),
}

class DocumentFileModule(FileHandleModule):
    
    def __init__(self):
        self.tables = {}


    @staticmethod
    def handledFileMimes() -> str or Iterable[str]:
        # Only PDF and Epub at this time
        return [
            'application/pdf',
            'application/epub*',
            # 'application/x-abiword',
            # 'application/vnd.oasis.opendocument.*',             # Opendocument
            # 'application/msword',                               # Word
            # 'application/vnd.ms-*',                             # Office documents (old)
            # 'application/vnd.openxmlformats-officedocument.*'   # Office document (OpenXML)
        ]

    def requiredModules(self) -> Iterable[str] or None:
        return [
            'CoreModule'
        ]

    # Database
    def getDatabaseSchema(self) -> str:
        return 'document'

    def defineTables(self, metadata: sqlalchemy.MetaData, configuration: ConfigHandler) -> None:
        
        coreModuleTables = configuration.getFileHandleModuleByName('CoreModule').getSharedTables()
        
        self.tables['file_document'] = sqlalchemy.Table('file_document', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, sqlalchemy.Sequence('file_document_id_seq'), primary_key=True),
            sqlalchemy.Column('id_file', sqlalchemy.Integer, sqlalchemy.ForeignKey(coreModuleTables['file'].c.id, ondelete='NO ACTION'), nullable=False),
            sqlalchemy.Column('title', sqlalchemy.String(511), index=True, unique=False, nullable=True),
            sqlalchemy.Column('author', sqlalchemy.String(511), index=True, unique=False, nullable=True),
            sqlalchemy.Column('pages', sqlalchemy.Integer, index=False, unique=False, nullable=True),
            sqlalchemy.Column('words', sqlalchemy.BigInteger, index=False, unique=False, nullable=True),
            sqlalchemy.Column('characters', sqlalchemy.BigInteger, index=False, unique=False, nullable=True)
        )

        self.tables['chapter'] = sqlalchemy.Table('chapter', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, sqlalchemy.Sequence('chapter_id_seq'), primary_key=True),
            sqlalchemy.Column('id_parent_chapter', sqlalchemy.Integer, sqlalchemy.ForeignKey('chapter.id', ondelete='CASCADE'), unique=False, nullable=True),
            sqlalchemy.Column('title', sqlalchemy.String(511), index=True, unique=False, nullable=False),
            sqlalchemy.Column('page', sqlalchemy.Integer, index=False, unique=False, nullable=True)
        )

        self.tables['meta_name'] = sqlalchemy.Table('meta_name', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, sqlalchemy.Sequence('meta_name_id_seq'), primary_key=True),
            sqlalchemy.Column('name', sqlalchemy.String(255), index=True, unique=True, nullable=False)
        )

        self.tables['meta_value'] = sqlalchemy.Table('meta_value', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, sqlalchemy.Sequence('meta_value_id_seq'), primary_key=True),
            sqlalchemy.Column('id_meta_name', sqlalchemy.Integer, sqlalchemy.ForeignKey(self.tables['meta_name'].c.id, ondelete='CASCADE'), nullable=False),
            sqlalchemy.Column('id_file_document', sqlalchemy.Integer, sqlalchemy.ForeignKey(self.tables['file_document'].c.id, ondelete='CASCADE'), nullable=False),
            sqlalchemy.Column('value', sqlalchemy.String(511), index=True, unique=False, nullable=False)
        )

    def getSharedTables(self) -> Dict[str, sqlalchemy.Table]:
        return self.tables.copy()

    def getDBQuerier(self, dbEngine: sqlalchemy.engine.Engine, appConfig: ConfigHandler) -> object:
        return DbQuerier(dbEngine, appConfig, self)

    # Processing
    def canHandle(self, fileDescriptor: FileDescriptor) -> bool:
        return True


    def handle(self, fileDescriptor: FileDescriptor, dbEngine: sqlalchemy.engine.Engine, appConfig: ConfigHandler) -> None:
        for pattern, processor in _processors.items():
            if fnmatch(name=fileDescriptor.mime, pat=pattern):
                processor.process(self, fileDescriptor, appConfig, dbEngine)
                return