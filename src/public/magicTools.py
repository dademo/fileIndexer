import logging
import atexit
import magic
from threading import Lock

logger = logging.getLogger('fileIndexer').getChild('public.magicTools')
MAGIC_FLAGS_DEFAULT = magic.MIME


ms = None

_lock = Lock()


def getMagic(ms_flags=MAGIC_FLAGS_DEFAULT):
    '''
        Loads magic library and returns a handle.

        It also registers a :func:`atexit.atexit` function.

        :returns: A loaded magic handle.
        :rtype: :class:`magic.Magic`
    '''
    
    global ms

    def free_magic():
        if ms != None:
            logger.info('Freeing libmagic')
            ms.close()
        

    if ms == None:
        logger.info('Loading libmagic configuration')
        ms = magic.open(ms_flags)
        ms.load()
        atexit.register(free_magic)
        logger.info('Done')

    ms.setflags(ms_flags)

    return ms


def acquireLock() -> bool:
    '''
        Acquire the modue lock.
    '''
    return _lock.acquire(blocking=True)

def releaseLock() -> None:
    '''
        Releases the module lock.
    '''
    return _lock.release()