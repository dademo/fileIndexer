#!/bin/env python3

from typing import Iterable, List, Any
from atexit import register
import logging
import sys
import os
from urllib.parse import urlparse

from lib.database import getInitializedDb
from lib.moduleLoader import loadModule
from lib.messageDispatcher import MessageDispatcher
from lib.configuration import moduleConfiguration
from public import FileHandleModule, FileSystemModule, ConfigHandler

import sqlalchemy
from lazy_streams import stream


logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', level=logging.INFO)

logger = logging.getLogger('fileIndexer')
#logging.getLogger('fileIndexer').setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
#logging.getLogger('sqlalchemy').setLevel(logging.INFO)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)


__defaultFileSystemModules = [ 'public.modules.LocalFileSystemModule' ]
__defaultFileHandleModules = [ 'public.modules.CoreModule' ]

def _unique(v: Iterable[Any]) -> List[Any]:
    '''
        Return unique values of iterable as a list (required for lazy_streams).

        :param v: The iterable to handle.
        :type v: [any]

        :returns: A list containing unique values.
        :rtype: [any]
    '''
    return list(set(v))


def loadAppConfig(configPath: str) -> ConfigHandler:
    '''
        Loads the application configuration with the required modules (default and specified in configuration).

        :param configPath: The configuration path to load (a ``.yaml`` file).
        :type configPath: str

        :returns: The application configuration.
        :rtype: ConfigHandler
    '''
    
    #appConfig = yaml.load(os.path.join(os.path.dirname(__file__) or '.', 'config.yaml'), Loader=yaml.FullLoader)
    appConfig = ConfigHandler.load(
        configPath,
        appPath=os.path.abspath(os.path.dirname(__file__) or '.')
    )

    appConfig._fileHandleModules = stream(_unique(__defaultFileHandleModules + (appConfig.get(moduleConfiguration['fileHandleModulesConfiguration'], False) or []))) \
        .map(lambda moduleName: loadModule(moduleName, FileHandleModule)) \
        .to_list()

    appConfig._fileSystemModules = stream(_unique(__defaultFileSystemModules + (appConfig.get(moduleConfiguration['fileSystemModulesConfiguration'], False) or []))) \
        .map(lambda moduleName: loadModule(moduleName, FileSystemModule)) \
        .to_list()

    return appConfig

## https://docs.python.org/fr/3/library/fnmatch.html
'''
def sqlalchemyMergeMetaDatas(metaDatas: List[sqlalchemy.MetaData]):

    mergedMetaDatas = sqlalchemy.MetaData()

    for metaData in metaDatas:
        for (table_name, table) in metaData.tables.items():
            mergedMetaDatas._add_table(table_name, table.schema, table)

    return mergedMetaDatas
'''

if __name__ == '__main__':
    
    appFileSystemModules = []
    appModules = []
    
    appConfig = loadAppConfig(configPath =    os.path.abspath(os.path.join(os.path.dirname(__file__) or '.', 'config.yaml')))
    dbEngine = getInitializedDb(appConfig)

    #db = sqlalchemy.create_engine('sqlite:///:memory:', encoding='utf-8', echo=True)
    #dbEngine = sqlalchemy.create_engine('sqlite:///db/core.db', encoding='utf-8', poolclass=sqlalchemy.pool.StaticPool, isolation_level=None)
    #dbEngine = sqlalchemy.create_engine('postgresql://postgres:postgres@localhost/fileIndexer', encoding='utf-8', poolclass=sqlalchemy.pool.StaticPool, isolation_level=None)
    #initializeDb(dbEngine, appModules, None)

    from pprint import pprint
    from public.modules.localFileSystemModule import LocalFileSystemModule

    fsModule = LocalFileSystemModule()
    fsModule.connect(urlparse('/home/dademo/Musique'), appConfig)
    #pprint(list(map(lambda fileDesc: fileDesc.getFileFullName(), fsModule.listFiles())))
    #print(list(map(lambda fileDesc: fileDesc.getFileStat(), fsModule.listFiles())))
    #import magic
    #print(list(map(lambda fileDesc: fileDesc.getFileMime(), fsModule.listFiles())))
    #print(list(map(lambda fileDesc: "%s: %s" % (fileDesc.getFileName(), fileDesc.getFileMime(ms_flags=magic.NONE)), fsModule.listFiles())))
    #print('-\n'.join(map(lambda fileDesc: "%s: %s|%s" % (fileDesc.getFileName(), fileDesc.getFileMime(), fileDesc.getFileMime(ms_flags=magic.NONE)), fsModule.listFiles())))
    
    logger.info('Handling files')
    messageDispatcher = MessageDispatcher(appModules, appConfig)
    for fileDecriptor in fsModule.listFiles():
        messageDispatcher.dispatch(fileDecriptor)
        # appModules[0].handle(fileDecriptor, dbEngine, appConfig)
