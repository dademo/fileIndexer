from public import FileDescriptor, ConfigHandler
import public.dbTools as dbTools
import logging

import sqlalchemy
from sqlalchemy.sql import select, func, and_

logger = logging.getLogger('fileIndexer').getChild('public.modules.coreModule.DbQuerier')


class DbQuerier(object):
    '''
        A helper to query and insert entities for the CoreModule.

        :param dbEngine: A SQLAlchemy DBEngine.
        :type dbEngine: sqlalchemy.engine.Engine
        :param moduleRef: A reference to the calling module (self).
        :type moduleRef: class:`modules.documentFileModule.module.DocumentFileModule`
    '''
    
    def __init__(self, dbEngine: sqlalchemy.engine.Engine, appConfig: ConfigHandler, moduleRef: 'DocumentFileModule'):
        self.dbEngine = dbEngine
        self.moduleRef = moduleRef
        self.table = moduleRef.getSharedTables()
        self.appConfig = appConfig
        coreModule = appConfig.getFileHandleModuleByName('CoreModule')
        self.coreModuleTables = coreModule.getSharedTables()
        self.coreModuleQuerier = coreModule.getDBQuerier(dbEngine, appConfig)


    def getChapterEntity(self, parentChapterEntity: dict or None, chapterTitle: str):
        '''
            __TODO__
        '''

        table = self.table

        parentChapterId = None
        if parentChapterEntity:
            parentChapterId = parentChapterEntity['id']
        
        s = select([
            table['chapter']
            ]).\
            where(and_(
                table['chapter'].c.id_parent_chapter == parentChapterId,
                table['chapter'].c.title == chapterTitle
            ))

        i = table['chapter'].insert().values(id_parent_chapter=parentChapterId, title=chapterTitle)
        
        return dbTools.getSingletonEntity(s, i, self.dbEngine)


    def getMetaNameEntity(self, metaName: str):
        '''
            Get the database value for the given meta name.

            :param filePath: The meta name to retrieve.
            :type filePath: str

            :return: A file path entity
            :rtype: dict
        '''

        table = self.table
        
        s = select([
            table['meta_name']
            ]).\
            where(table['meta_name'].c.name == metaName)

        i = table['meta_name'].insert().values(name=metaName)
        
        return dbTools.getSingletonEntity(s, i, self.dbEngine)


    def getMetaValueEntity(self, documentEntity: dict, metaNameEntity: dict, metaValue: str):
        '''
            __TODO__
        '''

        table = self.table
        
        s = select([
            table['meta_value']
            ]).\
            where(and_(
                    table['meta_value'].c.id_meta_name == metaNameEntity['id'],
                    table['meta_value'].c.id_file_document == documentEntity['id'],
                    table['meta_value'].c.value == str(metaValue)[:511]
            ))

        i = table['meta_value'].insert().values(
            id_meta_name=metaNameEntity['id'],
            id_file_document=documentEntity['id'],
            value=metaValue
        )
        
        return dbTools.getSingletonEntity(s, i, self.dbEngine)


    def getFileDocumentEntity(self,
        fileDescriptor: FileDescriptor,
        title: str,
        author: str,
        pageCount: int,
        wordCount: int,
        characterCount: int
    ) -> None:
        '''
            # TODO
        '''
        
        table = self.table
        coreModuleTables = self.coreModuleTables
        fileEntity = self.coreModuleQuerier.getFileInDatabase(fileDescriptor)
        
        s = select([
            table['file_document']
            ]).\
            where(and_(
                coreModuleTables['file'].c.id == fileEntity['id']
            ))

        i = table['file_document'].insert().values(
            id_file=fileEntity['id'],
            title=title,
            author=author,
            pages=pageCount,
            words=wordCount,
            characters=characterCount
        )
        
        return dbTools.getSingletonEntity(s, i, self.dbEngine, allowParallel=True)