import logging
from threading import Lock
from typing import Any

import sqlalchemy
from sqlalchemy.sql.expression import Select, Insert

logger = logging.getLogger('fileIndexer').getChild('public.dbTools')

_globalLock = Lock()


def getSingletonEntity(selectStatement: Select, insertStatement: Insert, dbEngine: sqlalchemy.engine.Engine, allowParallel: bool=False, _lock: bool=False):
    '''
        Get a singleton entity using the given selectStatement or insertStatement.

        :param selectStatement: A select statement to execute, used to check whether
                                the element exists and query the element if
                                `statement.returned_defaults` is False.
        :type selectStatement: :class:`sqlalchemy.sql.expression.select`
        :param insertStatement: An insert statement to execute to fill the database
                                with the missing values.
        :type insertStatement: :class:`sqlalchemy.sql.expression.insert`
        :param allowParallel: If we allow to insert without a lock. Can produce
                                :class:`sqlalchemy.exc.IntegrityError` on duplicate key.
        :type allowParallel: bool
        :param _lock: If we have to set up a lock when querying. Note that if this value
                        is set allowParallel is ignored and lock is always used.
        :type _lock: bool
        :param dbEngine: A SQLAlchemy database engine.
        :type dbEngine: :class:`sqlalchemy.engine.Engine`
    '''

    insertStatement.return_defaults()
    
    with dbEngine.connect() as dbConnection:
        if _lock:
            with _globalLock:
                
                entity = dbConnection.execute(selectStatement).first()

                if not entity:
                    stmt = dbConnection.execute(insertStatement)

                    if stmt.returned_defaults:
                        return dict(stmt.returned_defaults)
                    else:
                        return dict(dbConnection.execute(selectStatement).first())
                else:
                    return dict(entity)
        else:
            entity = dbConnection.execute(selectStatement).first()

            if not entity:
                if allowParallel:
                    stmt = dbConnection.execute(insertStatement)

                    if stmt.returned_defaults:
                        return dict(stmt.returned_defaults)
                    else:
                        return dict(dbConnection.execute(selectStatement).first())
                else:
                    # Entity not found. We have to insert and return it (inside a lock to avoid duplicate keys)
                    return getSingletonEntity(selectStatement, insertStatement, dbEngine, allowParallel=False, _lock=True)
            else:
                return dict(entity)
