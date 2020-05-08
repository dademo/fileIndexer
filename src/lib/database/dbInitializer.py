from public import FileHandleModule
from public.configHandler import ConfigHandler

from sqlalchemy import MetaData
from sqlalchemy.engine import Engine, Connection, Transaction

from typing import Iterable
import os


def initializeDb(dbEngine: Engine, configuration: ConfigHandler) -> None:
    '''
        Initialize the database with all the required tables (it should already
        have the required schemas).

        :param dbEngine: A :class:`sqlalchemy.engine.Engine` instance, a database connection.
        :param configuration: The application configuration.
    '''

    for module in configuration.getFileHandleModules():
        moduleMetaData = MetaData(schema=module.getDatabaseSchema())

        module.defineTables(moduleMetaData, configuration)

        moduleMetaData.create_all(dbEngine)

