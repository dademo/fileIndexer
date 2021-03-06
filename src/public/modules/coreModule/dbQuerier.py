from public import FileDescriptor
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
        :type moduleRef: class:`public.modules.coreModule.module.CoreModule`
    '''
    
    def __init__(self, dbEngine: sqlalchemy.engine.Engine, moduleRef: 'CoreModule'):
        self.dbEngine = dbEngine
        self.moduleRef = moduleRef
        self.table = moduleRef.getSharedTables()


    def haveBeenModified(self, fileDescriptor: FileDescriptor):
        '''
            Check whether the file have been modified since last execution (from
            the point of view of the coreModule). Used to inform other modules of
            a modification.
            
            :param fileDescriptor: A file descriptor to search in the database.
            :type fileDescriptor: :class:`public.fileDescriptor.FileDescriptor`

            :return: Whether the file have been modified since last execution.
            :rtype: bool
        '''
        table = self.table

        s = select([
                (table['file'].c.last_update == fileDescriptor.modificationDateTime).label('is_same_date')
            ]).\
            select_from(table['file'].join(table['file_path'])).\
            where(and_(
                table['file'].c.filename == fileDescriptor.name,
                table['file_path'].c.path == fileDescriptor.path,
            ))

        with self.dbEngine.connect() as dbConnection:
            result = dbConnection.execute(s).first()
            if result:
                return not result['is_same_date']
            else:
                return True


    def isFileInDatabase(self, fileDescriptor: FileDescriptor) -> bool:
        '''
            Check whether the file description is in the database.
            
            :param fileDescriptor: A file descriptor to search in the database.
            :type fileDescriptor: :class:`public.fileDescriptor.FileDescriptor`

            :return: Whether the file is in the database.
            :rtype: bool
        '''
        
        table = self.table

        s = select([
                func.count(table['file'].c.id).label('file_count')
            ]).\
            select_from(table['file'].join(table['file_path'])).\
            where(and_(
                table['file'].c.filename == fileDescriptor.name,
                table['file_path'].c.path == fileDescriptor.path,
            ))

        with self.dbEngine.connect() as dbConnection:
            return dbConnection.execute(s).first()['file_count'] > 0


    def getFileMimeEntity(self, fileMime: str):
        '''
            Get the database value for the given fileMime.

            :param fileMime: The file mime to retrieve.
            :type fileMime: str

            :return: A file mime entity
            :rtype: dict
        '''
        
        table = self.table
        
        s = select([
            table['file_mime']
            ]).\
            where(table['file_mime'].c.mime == fileMime)

        i = table['file_mime'].insert().values(mime=fileMime)
        
        return dbTools.getSingletonEntity(s, i, self.dbEngine, allowParallel=False)


    def getFileEncodingEntity(self, fileEncoding: str):
        '''
            Get the database value for the given fileEncoding.

            :param fileEncoding: The file encoding to retrieve.
            :type fileEncoding: str

            :return: A file encoding entity
            :rtype: dict
        '''
        
        table = self.table
        
        s = select([
            table['file_encoding']
            ]).\
            where(table['file_encoding'].c.encoding == fileEncoding)

        i = table['file_encoding'].insert().values(encoding=fileEncoding)
        
        return dbTools.getSingletonEntity(s, i, self.dbEngine, allowParallel=False)


    def getFilePathEntity(self, filePath: str, fileSchemeAndHost: str):
        '''
            Get the database value for the given filePath.

            :param filePath: The file path to retrieve.
            :type filePath: str
            :param fileSchemeAndHost: The file scheme and host to support multiple locations
            :type filePath: str

            :return: A file path entity
            :rtype: dict
        '''
        
        table = self.table
        
        s = select([
            table['file_path']
            ]).\
            where(table['file_path'].c.path == filePath)

        i = table['file_path'].insert().values(path=filePath, scheme_host=fileSchemeAndHost)
        
        return dbTools.getSingletonEntity(s, i, self.dbEngine, allowParallel=False)


    def getFileEntity(self, fileDescriptor: FileDescriptor, fileMimeEntity: any, fileEncodingEntity: any, filePathEntity: any):
        '''
            Add a file entity in the database.

            :param fileDescriptor: A file descriptor.
            :type fileDescriptor: :class:`public.fileDescriptor.FileDescriptor`
            :param fileMimeEntity: dict
            :type fileMimeEntity: A file mime entity.
            :param fileEncodingEntity: A file encoding entity
            :type fileEncodingEntity: dict
            :param filePathEntity: A file path entity.
            :type filePathEntity: dict

            :return: A file entity
            :rtype: dict
        '''
        
        table = self.table
        
        s = select([
            table['file']
            ]).\
            where(and_(
                table['file'].c.id_file_mime == fileMimeEntity['id'],
                table['file'].c.id_file_encoding == fileEncodingEntity['id'],
                table['file'].c.id_file_path == filePathEntity['id'],
                table['file'].c.filename == fileDescriptor.name
            ))

        i = table['file'].insert().values(
            id_file_mime=fileMimeEntity['id'],
            id_file_encoding=fileEncodingEntity['id'],
            id_file_path=filePathEntity['id'],
            filename=fileDescriptor.name,
            size_kilobyte=fileDescriptor.sizeKB,
            last_update=fileDescriptor.modificationDateTime,
            file_description=fileDescriptor.description
        )
        
        return dbTools.getSingletonEntity(s, i, self.dbEngine, allowParallel=True)

    def getFileInDatabase(self, fileDescriptor: FileDescriptor) -> None:
        '''
            Insert base file information in the database and return it.

            :param fileDescriptor: A file descriptor to get file informations.
            :type FileDescriptor: :class:`public.fileDescriptor.FileDescriptor`
        '''

        fileMimeEntity = self.getFileMimeEntity(fileDescriptor.mime)
        fileEncodingEntity = self.getFileEncodingEntity(fileDescriptor.encoding)
        filePathEntity = self.getFilePathEntity(fileDescriptor.path, fileDescriptor.schemeAndHost)
        return self.getFileEntity(fileDescriptor, fileMimeEntity, fileEncodingEntity, filePathEntity)