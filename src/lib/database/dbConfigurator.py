import logging

from public import ConfigHandler
from .dbConnector import getDbEngine
from .dbInitializer import initializeDb

import sqlalchemy
from sqlalchemy.engine import Engine

logger = logging.getLogger('fileIndexer').getChild('lib.database.dbConfigurator')

def getInitializedDb(configuration: ConfigHandler) -> Engine:
    '''
        Initialize a database connection and the required tables.

        :returns: A fully initialized database.
        :raises MissingDatabaseConfigurationException: No database connection is configured.
    '''

    logger.info('Establishing connection with the database')
    dbEngine = getDbEngine(configuration)
    logger.info('Done, connected with [%s]' % str(dbEngine.url))

    logger.info('Initializing database')
    initializeDb(dbEngine, configuration)
    logger.info('Initialization performed')

    return dbEngine