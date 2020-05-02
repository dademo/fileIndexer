from public import FileHandleModule, FileDescriptor
import public.dbTools as dbTools
import logging

import sqlalchemy
from sqlalchemy.sql import select, func, and_

logger = logging.getLogger('fileIndexer').getChild('public.modules.coreModule.DbQuerier')


class DbQuerier(object):
    
    def __init__(self, dbEngine: sqlalchemy.engine.Engine, moduleRef: FileHandleModule):
        self.dbEngine = dbEngine
        self.moduleRef = moduleRef
        self.table = moduleRef.getSharedTables()

    def isFileInDatabase(self, fileDescriptor: FileDescriptor) -> bool:
        
        table = self.table

        s = select([
                func.count(table['file'].c.id).label('file_count')
            ]).\
            select_from(table['file'].join(table['file_path'])).\
            where(and_(
                table['file'].c.filename == fileDescriptor.getFileName(),
                table['file_path'].c.path == fileDescriptor.getFilePath(),
            ))

        with self.dbEngine.connect() as dbConnection:
            return dbConnection.execute(s).first()['file_count'] > 0


    def getFileMimeEntity(self, fileMime: str):
        
        table = self.table
        
        s = select([
            table['file_mime']
            ]).\
            where(table['file_mime'].c.mime == fileMime)

        i = table['file_mime'].insert().values(mime=fileMime)
        
        return dbTools.getSingletonEntity(s, i, self.dbEngine)


    def getFileEncodingEntity(self, fileEncoding: str):
        
        table = self.table
        
        s = select([
            table['file_encoding']
            ]).\
            where(table['file_encoding'].c.encoding == fileEncoding)

        i = table['file_encoding'].insert().values(encoding=fileEncoding)
        
        return dbTools.getSingletonEntity(s, i, self.dbEngine)


    def getFilePathEntity(self, filePath: str):
        
        table = self.table
        
        s = select([
            table['file_path']
            ]).\
            where(table['file_path'].c.path == filePath)

        i = table['file_path'].insert().values(path=filePath)
        
        return dbTools.getSingletonEntity(s, i, self.dbEngine)


    def getFileEntity(self, fileDescriptor: FileDescriptor, fileMimeEntity: any, fileEncodingEntity: any, filePathEntity: any):
        
        table = self.table
        
        s = select([
            table['file']
            ]).\
            where(and_(
                table['file'].c.id_file_mime == fileMimeEntity['id'],
                table['file'].c.id_file_encoding == fileEncodingEntity['id'],
                table['file'].c.id_file_path == filePathEntity['id'],
                table['file'].c.filename == fileDescriptor.getFileName()
            ))

        i = table['file'].insert().values(
            id_file_mime=fileMimeEntity['id'],
            id_file_encoding=fileEncodingEntity['id'],
            id_file_path=filePathEntity['id'],
            filename=fileDescriptor.getFileName(),
            size_kilobyte=fileDescriptor.getFileSizeKB(),
            last_update=fileDescriptor.getModificationDateTime(),
            file_description=fileDescriptor.getFileDescription()
        )
        
        return dbTools.getSingletonEntity(s, i, self.dbEngine)

    def addFileInDatabase(self, fileDescriptor: FileDescriptor):
        
        fileMimeEntity = self.getFileMimeEntity(fileDescriptor.getFileMime())
        fileEncodingEntity = self.getFileEncodingEntity(fileDescriptor.getFileEncoding())
        filePathEntity = self.getFilePathEntity(fileDescriptor.getFilePath())
        #logger.info(fileDescriptor.getFileName())
        #logger.info(fileDescriptor.getFileDescription())
        fileEntity = self.getFileEntity(fileDescriptor, fileMimeEntity, fileEncodingEntity, filePathEntity)