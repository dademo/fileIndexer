import os
from threading import Thread, Timer
from fnmatch import fnmatch
from typing import List, Iterable
from threading import Lock
import itertools
import logging
import traceback

from lib.database import canDatabaseHandleParallelConnections

from public import FileHandleModule, FileSystemModule
from public.fileDescriptor import FileDescriptor
from public.configHandler import ConfigHandler
from public.configuration import moduleConfiguration

from multiprocessing.pool import ThreadPool
import multiprocessing.dummy
from multiprocessing.pool import ThreadPool

from sqlalchemy.engine import Engine

logger = logging.getLogger('fileIndexer').getChild('lib.MessageDispatcher')


class CachedFileDescriptorsIterator(object):
    '''
        A simple :class:`public.FileSystemModule` iterator that keep in cache
        the first returned values.

        Used instead of keeping values in a simple list, blocking the program
        while all files have not been listed by the module.
    '''
    
    def __init__(self, fileSystemModule: FileSystemModule, ignorePatterns: List[str], followSymlinks: bool):
        '''
        ..note::

            These parameters will be given to the
            :meth:`public.fileSystemModule.FileSystemModule.listFiles` method.

            
            :param fileSystemModule: The module which is listing files.
            :type fileSystemModule: public.fileSystemModule.FileSystemModule
            :param ignorePatterns: Patterns to ignore.
            :type ignorePatterns: List[str]
            :param followSymlinks: Does the listing follow links.
            :type followSymlinks: bool
        '''
        self._fileSystemModule = fileSystemModule
        self._ignorePatterns = ignorePatterns
        self._followSymlinks = followSymlinks
        self._cache = None
        self._iter = None
        self._iterPos = 0

    def __iter__(self):
        if not self._cache:
            self._iter = self._fileSystemModule.listFiles(ignorePatterns=self._ignorePatterns, followSymlinks=self._followSymlinks)
            self._cache = []
        else:
            self._iter = None
            self._iterPos = 0
        return self

    def __next__(self):
        if self._iter:
            v = next(self._iter)
            self._cache.append(v)
            return v
        else:
            self._iterPos += 1
            if self._iterPos == len(self._cache):
                raise StopIteration
            else:
                return self._cache[self._iterPos-1]

class MessageDispatcher(object):

    def __init__(self, appConfig: ConfigHandler):

        self.appConfig = appConfig

        self.threadPool = ThreadPool(appConfig.get(
            moduleConfiguration['moduleWorkersCount']))

        self._done = False
        self._showThreadLength = True

    def __del__(self):
        '''
            Closes the thread pool on close.
        '''
        self.threadPool.terminate()
        try:
            self.threadPool.join()
        except Exception as ex:
            logger.exception(ex)

    def setDone(self) -> None:
        '''
            Set the job done to ends file handling (this will wait for current
            jobs to have runned).

            This will stop the :meth:`public.messageDispatcher.MessageDispatcher.dispatch` method.
        '''
        self._done = True

    def dispatch(self, dbEngine: Engine, appConfig: ConfigHandler) -> None:
        '''
            Dispatch found files for each path configured.

            It handles parallel processing if available (depends on the data source type, if it handles parallel
            connections).
            :param dbEngine: A database connection.
            :type dbEngine: :class:`sqlalchemy.engine.Engine`
            :param dbEngine: The application configuration.
            :type dbEngine: :class:`public.configHandler.ConfigHandler`
        '''

        # import $(dbEngine.driver).threadsafety
        steps = appConfig.getDependencyTree()
        workResults = []
        ex = None
        actualModuleCallCount = 1
        totalModuleCallCount = len(list(itertools.chain(*steps)))
        allowParallelExecution = canDatabaseHandleParallelConnections(dbEngine)

        if not allowParallelExecution:
            logger.info(
                'Parallel execution will be disabled because the database API does not allow parallel connections')

        def _errCallback(err):
            # logger.error("An error occured :\n%s" % repr(err))
            logger.error("An error occured :\n%s" % repr(err))

        def waitAll():
            while len(workResults) > 0:
                if not self._done:
                    workResults.pop(0).wait()
                else:
                    #self.threadPool.close()
                    self.threadPool.terminate()
                    #self.threadPool._inqueue._queue.clear()
                    self.threadPool.join()
                    return

        def runHandle(currentModule: FileHandleModule, fileDescriptor: FileDescriptor):
            try:
                if any(map(
                    lambda _mime: fnmatch(fileDescriptor.mime, _mime),
                    self._module_mimes(currentModule)
                )):
                    if not self._done:
                        if currentModule.canHandle(fileDescriptor):
                            currentModule.handle(fileDescriptor, dbEngine, appConfig)
            except Exception as ex:
                logger.exception("An error occured while running module [%s] on file [%s]" % (currentModule.__class__, fileDescriptor.fullPath))

        def printJobStatus():
            if self._showThreadLength:
                Timer(5.0, printJobStatus).start()
                if len(workResults) > 0:
                    logger.info('%d files to process' % len(workResults))

        try:
            printJobStatus()
            for dataSource in self.appConfig.getDataSources():
                fileSystemModule = self.appConfig.getFileSystemModuleForDataSource(dataSource['path'])
                logger.info('Processing [%s]' % dataSource['path'])
                # Cache for file descriptors to avoid excessive calls to get mimes etc
                fileDescriptorIterator = CachedFileDescriptorsIterator(
                    fileSystemModule=fileSystemModule,
                    ignorePatterns=dataSource['ignorePatterns'],
                    followSymlinks=dataSource['followSymlinks']
                )
                actualModuleCallCount = 1

                for stepId in range(0, len(steps)):
                    logger.info('Processing step %(stepId)02d of %(stepLength)02d' % {
                                'stepId': stepId+1, 'stepLength': len(steps)})
                    step = steps[stepId]

                    for currentModule in step:
                        logger.info('[%(actualModuleCallCount)02d of %(totalModuleCallCount)02d] Running module %(moduleName)s' % {
                            'actualModuleCallCount':    actualModuleCallCount,
                            'totalModuleCallCount':     totalModuleCallCount,
                            'moduleName':               currentModule.__class__.__name__,
                        })

                        for fileDescriptor in fileDescriptorIterator:
                            if not self._done:
                                if allowParallelExecution:
                                    workResults.append(
                                        self.threadPool.apply_async(
                                            runHandle,
                                            args=(currentModule, fileDescriptor),
                                            error_callback=_errCallback
                                        )
                                    )
                                else:
                                    # Synchronous call
                                    try:
                                        runHandle(currentModule, fileDescriptor)
                                    except Exception as ex:
                                        _errCallback(ex)
                            else:
                                logger.info('Closing working threads')
                                #self.threadPool.close()
                                self.threadPool.terminate()
                                self.threadPool.join()
                                return

                        logger.info('Jobs prepared, waiting for all to complete ...')
                        # We wait for all jobs to process before the next step
                        waitAll()
                        logger.info('Done')
                        if self._done:
                            return

                        actualModuleCallCount += 1

        except Exception as _ex:
            ex = _ex
            logger.info("Waiting for all to close (%d elements)" %
                        len(workResults))
            waitAll()
            # Terminating pool avoid being hung when shutdown
            self.threadPool.terminate()
        finally:
            self._showThreadLength = False
            if ex:
                raise ex

    def _module_mimes(self, module: FileHandleModule) -> List[str]:
        '''
            Ensure to get a list of handled mimes from a module.

            :returns: A list of handled mimes.
            :rtype: list[str]
        '''
        mimes = module.handledFileMimes()

        if isinstance(mimes, str):
            mimes = [mimes]

        return mimes
