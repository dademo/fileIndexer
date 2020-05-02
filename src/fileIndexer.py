#!/bin/env python3

from typing import List
from atexit import register
import logging
import sys
import os
import yaml

from lib.dbInitializer import initializeDb
from lib.moduleLoader import loadModule
from public import FileHandleModule, FileSystemModule
from urllib.parse import urlparse

import sqlalchemy


logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', level=logging.INFO)
#logging.getLogger('fileIndexer').setLevel(logging.INFO)
logging.getLogger('fileIndexer').setLevel(logging.DEBUG)
#logging.getLogger('sqlalchemy').setLevel(logging.INFO)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

## https://docs.python.org/fr/3/library/fnmatch.html

def sqlalchemyMergeMetaDatas(metaDatas: List[sqlalchemy.MetaData]):

    mergedMetaDatas = sqlalchemy.MetaData()

    for metaData in metaDatas:
        for (table_name, table) in metaData.tables.items():
            mergedMetaDatas._add_table(table_name, table.schema, table)

    return mergedMetaDatas

if __name__ == '__main__':
    
    appModules = []

    
    appConfig = yaml.load(os.path.join(os.path.dirname(__file__) or '.', 'config.yaml'))

    for moduleName in [
        'public.modules.CoreModule'
    ] + []:
        appModules.append(loadModule(moduleName, FileHandleModule))

    #db = sqlalchemy.create_engine('sqlite:///:memory:', encoding='utf-8', echo=True)
    dbEngine = sqlalchemy.create_engine('sqlite:///db/core.db', encoding='utf-8', poolclass=sqlalchemy.pool.StaticPool, isolation_level=None)
    initializeDb(dbEngine, appModules, None)

    from pprint import pprint
    from public.modules.localFileSystemModule import LocalFileSystemModule

    fsModule = LocalFileSystemModule()
    fsModule.connect(urlparse('/home/dademo/Musique'), appConfig)
    #pprint(list(map(lambda fileDesc: fileDesc.getFileFullName(), fsModule.listFiles())))
    #print(list(map(lambda fileDesc: fileDesc.getFileStat(), fsModule.listFiles())))
    import magic
    #print(list(map(lambda fileDesc: fileDesc.getFileMime(), fsModule.listFiles())))
    #print(list(map(lambda fileDesc: "%s: %s" % (fileDesc.getFileName(), fileDesc.getFileMime(ms_flags=magic.NONE)), fsModule.listFiles())))
    #print('-\n'.join(map(lambda fileDesc: "%s: %s|%s" % (fileDesc.getFileName(), fileDesc.getFileMime(), fileDesc.getFileMime(ms_flags=magic.NONE)), fsModule.listFiles())))
    for fileDecriptor in fsModule.listFiles():
        appModules[0].handle(fileDecriptor, dbEngine, appConfig)
