
from typing import Iterable, Dict

from public import FileHandleModule, ConfigHandler, FileDescriptor

import sqlalchemy


class DocumentFileModule(FileHandleModule):
    
    def __init__(self):
        self.tables = {}


    @staticmethod
    def handledFileMimes() -> str or Iterable[str]:
        return [
            'application/epub*',
            'application/pdf',
            'application/x-abiword',
            'application/vnd.oasis.opendocument.*',             # Opendocument
            'application/msword',                               # Word
            'application/vnd.ms-*',                             # Office documents (old)
            'application/vnd.openxmlformats-officedocument.*'   # Office document (OpenXML)
        ]

    def requiredModules(self) -> Iterable[str] or None:
        return [
            'CoreModule'
        ]

    # Database
    def getDatabaseSchema(self) -> str:
        return 'document'

    def defineTables(self, metadata: sqlalchemy.MetaData, configuration: ConfigHandler) -> None:

        self.tables['file_document'] = sqlalchemy.Table('file_document', metadata,
            sqlalchemy.Column('id', sqlalchemy.Integer, sqlalchemy.Sequence('file_document_id_seq'), primary_key=True),
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

    def getSharedTables(self) -> Dict[str, sqlalchemy.Table]:
        return self.tables

    # Processing
    def canHandle(self, fileDescriptor: FileDescriptor) -> bool:
        return True


    def handle(self, fileDescriptor: FileDescriptor, dbEngine: sqlalchemy.engine.Engine, haveBeenModified: bool) -> None:
        with fileDescriptor.open() as _file:
            try:
                pass
                # print(mutagenFile)
                # print(mutagenFile.info)
                # print(mutagenFile.tags)
            except Exception as ex:
                print('Got exception [%s]' % repr(ex))
                print('Error with file [%s]' % fileDescriptor.fullPath)
        pass