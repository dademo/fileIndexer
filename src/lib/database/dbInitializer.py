from public import FileHandleModule
from public.configHandler import ConfigHandler

from sqlalchemy import MetaData
from sqlalchemy.engine import Engine, Connection, Transaction

from typing import Iterable
import os
import logging

logger = logging.getLogger('fileIndexer').getChild('lib.database.dbInitializer')


def _mergeMetadata(metas: Iterable[MetaData]) -> MetaData:

    globalMetaData = MetaData()

    for metaData in metas:
        for (tableName, table) in metaData.tables.items():
            globalMetaData._add_table(table.name, table.schema, table)

    return globalMetaData


def initializeDb(dbEngine: Engine, configuration: ConfigHandler) -> None:
    '''
        Initialize the database with all the required tables (it should already
        have the required schemas).

        :param dbEngine: A :class:`sqlalchemy.engine.Engine` instance, a database connection.
        :param configuration: The application configuration.
    '''

    allMetas = []
    for stepModules in configuration.getDependencyTree():
        for _module in stepModules:
            moduleMetaData = MetaData(schema=_module.getDatabaseSchema())

            _module.defineTables(moduleMetaData, configuration)

            allMetas.append(moduleMetaData)

    globalMetaData = _mergeMetadata(allMetas)
    globalMetaData.create_all(dbEngine)

