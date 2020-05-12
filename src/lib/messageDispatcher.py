import os
from threading import Thread
from fnmatch import fnmatch
from typing import List, Iterable
from threading import Lock
import itertools
import logging
import traceback

from lib.configuration import moduleConfiguration

from public import FileHandleModule, FileSystemModule
from public.fileDescriptor import FileDescriptor
from public.configHandler import ConfigHandler

from multiprocessing.pool import ThreadPool
import multiprocessing.dummy
#from multiprocessing.dummy import DummyProcess
from multiprocessing.pool import ThreadPool

from sqlalchemy.engine import Engine

logger = logging.getLogger('fileIndexer').getChild('lib.MessageDispatcher')


class MessageDispatcher(object):
    
    def __init__(self, appConfig: ConfigHandler):

        self.appConfig = appConfig

        self.threadPool = ThreadPool(appConfig.get(moduleConfiguration['moduleWorkersCount']))
        
        self._done = False

    def __del__(self):
        self.threadPool.close()
        try:
            self.threadPool.join()
        except Exception as ex:
            logger.exception(ex)


    def setDone(self):
        print('setDone')
        self._done = True


    def dispatch(self, fileSystemModule: FileSystemModule, steps: List[List[FileHandleModule]], dbEngine: Engine) -> None:

        def _errCallback(err):
            logger.error("An error occured :\n%s" % repr(err))


        # import $(dbEngine.driver).threadsafety
        workResults = []
        ex = None
        
        try:
            coreModule = list(filter(lambda m: m.__class__.__name__ == 'CoreModule', list(itertools.chain(*steps))))[0]
        except IndexError:
            coreModule = None

        if not coreModule:
            logger.debug('CoreModule is not loaded')

        try:
            for stepId in range(0, len(steps)):
                if self._done:
                    break
                logger.info('Processing step %02d of %02d' % (stepId+1, len(steps)))
                step = steps[stepId]

                for module in step:
                    if self._done:
                        break
                    logger.debug('Running module [%s]' % repr(module))
                    for fileDescriptor in filter(
                        lambda _fileDescriptor: any([fnmatch(_fileDescriptor.getFileMime(), moduleMime) for moduleMime in self._module_mimes(module)]),
                        fileSystemModule.listFiles()):

                        if not self._done:
                            if module.canHandle(fileDescriptor):

                                if coreModule:
                                    haveBeenModified = coreModule.haveBeenModified(fileDescriptor, dbEngine)
                                else:
                                    haveBeenModified = True

                                workResults.append(
                                    self.threadPool.apply_async(module.handle, args=(fileDescriptor, dbEngine, haveBeenModified), error_callback=_errCallback)
                                    #self.threadPool.apply(module.handle, args=(fileDescriptor, dbEngine, haveBeenModified))
                                )
                        else:
                            break
                
                # We wait for all jobs to process before the next step
                while len(workResults) > 0 and not self._done:
                    workResults.pop(0).wait()

        except Exception as _ex:
            ex = _ex
            logger.info("Waiting for all to close (%d elements)" % len(workResults))
            while len(workResults) > 0:
                workResults.pop(0).wait()
            # Terminating pool avoid being hung when shutdown
            self.threadPool.terminate()
                
        if ex:
            raise ex


    def _module_mimes(self, module: FileHandleModule) -> Iterable[str]:

        mimes = module.handledFileMimes()

        if isinstance(mimes, str):
            mimes = [ mimes ]

        return mimes