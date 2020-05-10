import os
from threading import Thread
import queue
from fnmatch import fnmatch
from typing import List, Iterable

from lib.configuration import moduleConfiguration

from public import FileHandleModule
from public.fileDescriptor import FileDescriptor
from public.configHandler import ConfigHandler

from multiprocessing.pool import ThreadPool
import multiprocessing.dummy
#from multiprocessing.dummy import DummyProcess
from multiprocessing.pool import ThreadPool

from sqlalchemy.engine import Engine


class MessageDispatcher(object):
    
    def __init__(self, appConfig: ConfigHandler):

        self.appConfig = appConfig

        self.threadPool = ThreadPool(appConfig.get(moduleConfiguration['moduleWorkersCount']))
        
        self.done = False


    def __del__(self):
        self.threadPool.close()


    def setDone(self):
        self.done = True


    def run(self):
        
        while not self.done:
            try:
                value = self.queue.get(block=True, timeout=1)
                self.dispatch(value)
            except queue.Empty:
                pass


    def dispatch(self, value: FileDescriptor, dbEngine: Engine) -> None:
        # TODO: Make a requirement tree
        for module in filter(
            lambda _module: any([fnmatch(value.getFileMime(), moduleMime) for moduleMime in self._module_mimes(_module)]),
            self.appConfig.getFileHandleModules()):
            if module.canHandle(value):
                # TODO: Edit haveBeenModified parameter
                module.handle(value, dbEngine, False)
                # module.getQueue.put(value)
                pass

    def closeAll(self):
        pass

    def _module_mimes(self, module: FileHandleModule) -> Iterable[str]:

        mimes = module.handledFileMimes()

        if isinstance(mimes, str):
            mimes = [ mimes ]

        return mimes