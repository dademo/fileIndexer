import logging
import atexit
import magic

logger = logging.getLogger('fileIndexer').getChild('public.magicTools')
MAGIC_FLAGS_DEFAULT = magic.MIME


ms = None

def getMagic(ms_flags=MAGIC_FLAGS_DEFAULT):
    
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