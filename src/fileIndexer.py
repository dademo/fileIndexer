#!/bin/env python3

from typing import Iterable, List, Any
from atexit import register
import logging
import sys
import os
import signal

from lib.database import getInitializedDb
from lib.moduleLoader import loadModule
from lib.messageDispatcher import MessageDispatcher
from lib.configuration import moduleConfiguration
from lib.dependencyTreeMaker import buildDependencyTree
from public import FileHandleModule, FileSystemModule, ConfigHandler

import sqlalchemy


logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', level=logging.INFO)

logger = logging.getLogger('fileIndexer')
#logging.getLogger('fileIndexer').setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)
#logging.getLogger('sqlalchemy').setLevel(logging.INFO)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)


__defaultFileSystemModules = [ 'public.modules.LocalFileSystemModule' ]
__defaultFileHandleModules = [ 'public.modules.CoreModule' ]


def loadApplicationConfiguration(configPath: str) -> ConfigHandler:
    '''
        Loads the application configuration and loads the configured modules
        (default and specified in configuration).

        :param configPath: The configuration path to load (a ``.yaml`` file).
        :type configPath: str

        :returns: The application configuration.
        :rtype: ConfigHandler
    '''
    
    applicationConfiguration = ConfigHandler.load(
        configPath,
        appPath=os.path.abspath(os.path.dirname(__file__) or '.')
    )

    applicationConfiguration._fileHandleModules = list(
        map(
            lambda moduleName: loadModule(moduleName, FileHandleModule),
            set(__defaultFileHandleModules + applicationConfiguration.get(moduleConfiguration['fileHandleModulesConfiguration']))
        )
    )

    applicationConfiguration._fileSystemModules = list(
        map(
            lambda moduleName: loadModule(moduleName, FileSystemModule),
            set(__defaultFileSystemModules + applicationConfiguration.get(moduleConfiguration['fileSystemModulesConfiguration']))
        )
    )

    applicationConfiguration._appDataSourcesCfg = moduleConfiguration['appDataSources']

    return applicationConfiguration


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
    
    # Values
    applicationConfiguration = None
    dbEngine = None
    messageDispatcher = None

    def onAppClose(signum, stack):
        logger.debug('onAppClose: %s:%s' % (signum, stack))
        logger.info("Catched end signal")
        # Waiting for the dispatcher to end
        if messageDispatcher:
            messageDispatcher.setDone()
            

    signal.signal(signal.SIGINT, onAppClose)
    signal.signal(signal.SIGTERM, onAppClose)
    
    applicationConfiguration = loadApplicationConfiguration(configPath = os.path.abspath(os.path.join(os.path.dirname(__file__) or '.', 'config.yaml')))
    dbEngine = getInitializedDb(applicationConfiguration)


    # fsModule = LocalFileSystemModule()
    # fsModule.connect(urlparse('/home/dademo/Musique'), applicationConfiguration)
    
    executionSteps = buildDependencyTree(applicationConfiguration.getFileHandleModules())

    logger.debug('Handling files')

    messageDispatcher = MessageDispatcher(applicationConfiguration)

    # threadsafety

    messageDispatcher.dispatch(executionSteps, dbEngine)

    exit(0)
