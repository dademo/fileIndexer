import importlib
import logging

from sqlalchemy.engine import Engine


logger = logging.getLogger('fileIndexer').getChild('lib.database.tools')

def getDbEngineThreadSafety(dbEngine: Engine) -> int:
    '''
        Returns the loaded dbEngine threadsafety value.

        If an error occurs, will return 0.


        .. note::
            Threadsafecty values as extracted from :pep:`249#threadsafety`.

            +-----------------------------------------------------------------------+
            | threadsafety |                        Meaning                         |
            +==============+========================================================+
            |      0       | Threads may not share the module.                      |
            +-----------------------------------------------------------------------+
            |      1       | Threads may share the module, but not connections.     |
            +-----------------------------------------------------------------------+
            |      2       | Threads may share the module and connections.          |
            +-----------------------------------------------------------------------+
            |      3       | Threads may share the module, connections and cursors. |
            +-----------------------------------------------------------------------+
        

        :param dbEngine: A database connection.
        :type dbEngine: :class:`sqlalchemy.engine.Engine`

        :return: The dbapi threadsafety or 0 by default.
        :rtype: int
    '''

    try:
        _module = importlib.import_module(str(dbEngine.driver))
        if 'threadsafety' in dir(_module):
            return _module.threadsafety
        else:
            return 0
    except (ImportError, ImportWarning) as ex:
        logger.debug(repr(ex))
        return 0
        

def canDatabaseHandleParallelConnections(dbEngine: Engine) -> bool:
    '''
        Returns whether the connection can handle parallel connections
        (threadSafety == 2 for the dbi api).


        :param dbEngine: A database connection.
        :type dbEngine: :class:`sqlalchemy.engine.Engine`

        :return: Whether the dbi api can handle parallel connections.
        :rtype: bool
    '''
    return getDbEngineThreadSafety(dbEngine) >= 2