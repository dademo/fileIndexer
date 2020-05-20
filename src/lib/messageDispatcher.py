import os
from threading import Thread
from fnmatch import fnmatch
from typing import List, Iterable
from threading import Lock
import itertools
import logging
import traceback

from lib.configuration import moduleConfiguration
from lib.database import canDatabaseHandleParallelConnections

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

        self.threadPool = ThreadPool(appConfig.get(
            moduleConfiguration['moduleWorkersCount']))

        self._done = False

    def __del__(self):
        '''
            Closes the thread pool on close.
        '''
        self.threadPool.close()
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

    def dispatch(self, steps: List[List[FileHandleModule]], dbEngine: Engine) -> None:
        '''
            Dispatch found files for each path configured.

            It handles parallel processing if available (depends on the data source type, if it handles parallel
            connections).

            :param steps: Steps to execute. A step is a list of :class:`public.fileHandleModule.FileHandleModule`
                            to process.
            :type steps: List[List[:class:`public.fileHandleModule.FileHandleModule`]]
            :param dbEngine: A database connection.
            :type dbEngine: :class:`sqlalchemy.engine.Engine`
        '''

        # import $(dbEngine.driver).threadsafety
        workResults = []
        ex = None
        actualModuleCallCount = 1
        totalModuleCallCount = len(list(itertools.chain(
            *steps))) * len(self.appConfig.getDataSources())
        allowParallelExecution = canDatabaseHandleParallelConnections(dbEngine)

        if not allowParallelExecution:
            logger.info(
                'Parallel execution will be disabled because the database API does not allow parallel connections')

        def _errCallback(err):
            logger.error("An error occured :\n%s" % repr(err))

        def wait_all():
            while len(workResults) > 0:
                if not self._done:
                    workResults.pop(0).wait()
                else:
                    #self.threadPool.close()
                    self.threadPool.terminate()
                    #self.threadPool._inqueue._queue.clear()
                    self.threadPool.join()
                    return

        def runHandle(coreModule, currentModule, fileDescriptor):
            if any(map(
                lambda _mime: fnmatch(fileDescriptor.getFileMime(), _mime),
                self._module_mimes(currentModule)
            )):
                if not self._done:
                    if currentModule.canHandle(fileDescriptor):

                        if coreModule:
                            haveBeenModified = coreModule.haveBeenModified(
                                fileDescriptor, dbEngine)
                        else:
                            haveBeenModified = True

                        currentModule.handle(
                            fileDescriptor, dbEngine, haveBeenModified)

        try:
            coreModule = list(filter(lambda m: m.__class__.__name__ ==
                                     'CoreModule', list(itertools.chain(*steps))))[0]
        except IndexError:
            coreModule = None

        if not coreModule:
            logger.debug('CoreModule is not loaded')

        try:
            for stepId in range(0, len(steps)):
                logger.info('Processing step %(stepId)02d of %(stepLength)02d' % {
                            'stepId': stepId+1, 'stepLength': len(steps)})
                step = steps[stepId]

                for dataSource in self.appConfig.getDataSources():
                    fileSystemModule = self.appConfig.getFileSystemModuleForDataSource(
                        dataSource['path'])
                    logger.info('Processing [%s]' % dataSource['path'])
                    logger.info('%d files' % len(list(fileSystemModule.listFiles(ignorePatterns=dataSource['ignorePatterns'], followSymlinks=dataSource['followSymlinks']))))

                    for currentModule in step:
                        logger.info('[%(actualModuleCallCount)03d-%(totalModuleCallCount)03d] Running module %(moduleName)s' % {
                            'actualModuleCallCount':    actualModuleCallCount,
                            'totalModuleCallCount':     totalModuleCallCount,
                            'moduleName':               currentModule.__class__.__name__,
                        })

                        for fileDescriptor in fileSystemModule.listFiles(ignorePatterns=dataSource['ignorePatterns'], followSymlinks=dataSource['followSymlinks']):
                            if not self._done:
                                if allowParallelExecution:
                                    workResults.append(
                                        self.threadPool.apply_async(runHandle, args=(
                                            coreModule, currentModule, fileDescriptor), error_callback=_errCallback)
                                        #self.threadPool.apply(module.handle, args=(fileDescriptor, dbEngine, haveBeenModified))
                                    )
                                else:
                                    # Single call
                                    try:
                                        runHandle(
                                            coreModule, currentModule, fileDescriptor)
                                    except Exception as ex:
                                        _errCallback(ex)
                            else:
                                logger.info('Closing working threads')
                                #self.threadPool.close()
                                self.threadPool.terminate()
                                self.threadPool.join()
                                return

                        logger.info('Job prepared, waiting for all to complete ...')
                        # We wait for all jobs to process before the next step
                        wait_all()
                        logger.info('Done')
                        if self._done:
                            return

                        actualModuleCallCount += 1

                        '''
                        for fileDescriptor in filter(
                                lambda _fileDescriptor: any([fnmatch(_fileDescriptor.getFileMime(), moduleMime)
                                                             for moduleMime in self._module_mimes(module)]),
                                fileSystemModule.listFiles()):

                            if not self._done:
                                if module.canHandle(fileDescriptor):

                                    if coreModule:
                                        haveBeenModified = coreModule.haveBeenModified(
                                            fileDescriptor, dbEngine)
                                    else:
                                        haveBeenModified = True

                                    if allowParallelExecution:
                                        workResults.append(
                                            self.threadPool.apply_async(module.handle, args=(
                                                fileDescriptor, dbEngine, haveBeenModified), error_callback=_errCallback)
                                            #self.threadPool.apply(module.handle, args=(fileDescriptor, dbEngine, haveBeenModified))
                                        )
                                    else:
                                        # Single call
                                        try:
                                            module.handle(
                                                fileDescriptor, dbEngine, haveBeenModified)
                                        except Exception as ex:
                                            _errCallback(ex)
                            else:
                                return
                        '''

        except Exception as _ex:
            ex = _ex
            logger.info("Waiting for all to close (%d elements)" %
                        len(workResults))
            wait_all()
            # Terminating pool avoid being hung when shutdown
            self.threadPool.terminate()

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
