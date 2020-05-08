from threading import Thread
import queue
from fnmatch import fnmatch
from typing import List, Iterable

from public import FileHandleModule
from public.fileDescriptor import FileDescriptor
from public.configHandler import ConfigHandler

from multiprocessing.pool import ThreadPool
import multiprocessing.dummy
#from multiprocessing.dummy import DummyProcess
from multiprocessing.pool import ThreadPool


class MessageDispatcher(object):
    
    def __init__(self, modules: List[FileHandleModule], config: ConfigHandler):

        self.modules = modules

        self.threadPool = ThreadPool(config.get('global.workersCount', raiseException=False))
        
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


    def dispatch(self, value: FileDescriptor) -> None:
        for module in filter(lambda module: fnmatch(value.getFileMime(), self._module_mimes(module)), self.modules):
            if module.canHandle(value):
                # module.getQueue.put(value)
                pass

    def closeAll(self):
        pass

    def _module_mimes(self, module: FileHandleModule) -> Iterable[str]:

        mimes = module.handledFileMimes()

        if isinstance(mimes, str):
            mimes = [ mimes ]

        return mimes