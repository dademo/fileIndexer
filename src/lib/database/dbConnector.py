import os
from typing import Iterable

from public.configHandler import ConfigHandler
from public.configuration import dbConfiguration
from .exceptions import MissingDatabaseConfigurationException

import sqlalchemy
from sqlalchemy.engine import Engine


#__sqliteConnectionPattern = """sqlite:///%(databaseAbsolutePath)s"""
__sqliteMemoryConnectionPattern = """sqlite://"""


def __getDatabaseSchemas(configuration: ConfigHandler) -> Iterable[str]:
    return list(
        map(
            lambda fileHandleModule: fileHandleModule.getDatabaseSchema(),
            configuration.getFileHandleModules()
        )
    )

def getDbEngine(configuration: ConfigHandler) -> Engine:
    '''
        Initialize a database connection. This database is ready to be exploited by the application
        (with schemas declared by configured modules).
        
        :param configuration: A :class:`public.configHandler.ConfigHandler` instance, having app configuration.

        :returns: A :class:`sqlalchemy.engine.Engine` instance.
        :raises MissingDatabaseConfigurationException: No database connection is configured.
    '''

    sqliteDbBasePath = configuration.get(dbConfiguration['sqliteConfigPath'])

    if sqliteDbBasePath:
        if os.path.isabs(sqliteDbBasePath):
            absoluteSQLiteDbBasePath = sqliteDbBasePath
        else:
            absoluteSQLiteDbBasePath = os.path.join(configuration.getAppPath() or os.path.abspath(os.path.join('..', '..')), sqliteDbBasePath)

        # Ensure the directory exists
        if not os.path.exists(absoluteSQLiteDbBasePath):
            os.makedirs(absoluteSQLiteDbBasePath)

        # Creating the core schema
        #dbEngine = sqlalchemy.create_engine(__sqliteConnectionPattern % { 'databaseAbsolutePath': os.path.join(absoluteSQLiteDbBasePath, 'core.db') })
        dbEngine = sqlalchemy.create_engine(__sqliteMemoryConnectionPattern)

        # Creating all the required SQLite databases (= schema)
        with dbEngine.begin() as dbConnection:
            for schema in __getDatabaseSchemas(configuration):
                dbConnection.execute('''ATTACH DATABASE '%(databasePath)s' AS "%(schema)s"''' % {
                    'databasePath': os.path.join(absoluteSQLiteDbBasePath, '%s.db' % schema),
                    'schema': schema
                })

        return dbEngine

    else:
        # Trying with an external database
        connectionString = configuration.get(dbConfiguration['dbConnectionString'])

        if not connectionString:
            raise MissingDatabaseConfigurationException('No database connection found. You should configure it inside the config.yaml file at paths [%s] or [%s]' % (
                dbConfiguration['sqliteConfigPath'],
                dbConfiguration['dbConnectionString'],
            ))

        dbEngine = sqlalchemy.create_engine(connectionString)

        # Ensure schema exists
        with dbEngine.begin() as dbConnection:
            for schema in __getDatabaseSchemas(configuration):
                dbConnection.execute('''
                    CREATE SCHEMA IF NOT EXISTS %(schema)s
                ''' % { 'schema': schema })

        return dbEngine

