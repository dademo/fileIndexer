from abc import ABC, abstractmethod

from public import FileDescriptor, ConfigHandler

import sqlalchemy


class DocumentFileProcessor(ABC):
    
    @abstractmethod
    def process(self, documentFileModule: 'DocumentFileModule', fileDescriptor: FileDescriptor, appConfig: ConfigHandler, dbEngine: sqlalchemy.engine.Engine):
        pass