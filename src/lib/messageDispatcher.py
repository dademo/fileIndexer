from threading import Thread
import queue
from fnmatch import fnmatch
from typing import List, Iterable

from public import FileHandleModule
import public.queueHandler as queueHandler
from public.fileDescriptor import FileDescriptor


class MessageDispatcher(Thread):
    
    def __init__(self, modules: List[FileHandleModule]):

        self.modules = modules

        self.done = False
        self.queue = queueHandler.getAppInputQueue()


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


    def _module_mimes(self, module: FileHandleModule) -> Iterable[str]:

        mimes = module.handledFileMimes()

        if isinstance(mimes, str):
            mimes = [ mimes ]

        return mimes