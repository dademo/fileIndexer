import logging

import sqlalchemy
from sqlalchemy.sql.expression import Select, Insert

logger = logging.getLogger('fileIndexer').getChild('public.dbTools')


def getSingletonEntity(selectStatement, insertStatement, dbEngine: sqlalchemy.engine.Engine):
    '''
        Get a singleton entity using the given selectStatement or insertStatement.

        :param selectStatement: A select statement to execute, used to check wether
                                the element exists and query the element if
                                `statement.returned_defaults` is False.
        :type selectStatement: :class:`sqlalchemy.sql.expression.select`
        :param insertStatement: An insert statement to execute to fill the database
                                with the missing values.
        :type insertStatement: :class:`sqlalchemy.sql.expression.insert`
        :param dbEngine: A SQLAlchemy database engine.
        :type dbEngine: :class:`sqlalchemy.engine.Engine`
    '''

    insertStatement.return_defaults()

    with dbEngine.connect() as dbConnection:
        entity = dbConnection.execute(selectStatement).first()
        if not entity:
            logger.debug('Entity not found, adding...')
            stmt = dbConnection.execute(insertStatement)

            if stmt.returned_defaults:
                return dict(stmt.returned_defaults)
            else:
                return dict(dbConnection.execute(selectStatement).first())
        else:
            return dict(entity)