import logging

import sqlalchemy
from sqlalchemy.sql.expression import Select, Insert

logger = logging.getLogger('fileIndexer').getChild('public.dbTools')


def getSingletonEntity(selectStatement, insertStatement, dbEngine: sqlalchemy.engine.Engine):

    insertStatement.return_defaults()

    with dbEngine.connect() as dbConnection:
        entity = dbConnection.execute(selectStatement).first()
        if not entity:
            logger.debug('No entity found, adding...')
            stmt = dbConnection.execute(insertStatement)

            if stmt.returned_defaults:
                return dict(stmt.returned_defaults)
            else:
                return dict(dbConnection.execute(selectStatement).first())
        else:
            return dict(entity)