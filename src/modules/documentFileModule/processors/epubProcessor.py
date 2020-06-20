import logging

from public import FileDescriptor, ConfigHandler
from modules.documentFileModule import DocumentFileProcessor, dbQuerier

import sqlalchemy

logger = logging.getLogger('fileIndexer').getChild('modules.documentFileModule.processors.EpubProcessor')


class EpubProcessor(DocumentFileProcessor):
    
    def process(self, documentFileModule: 'DocumentFileModule', fileDescriptor: FileDescriptor, appConfig: ConfigHandler, dbEngine: sqlalchemy.engine.Engine):
        with fileDescriptor.open() as _file:
            #pdfDocument = PdfFileReader(stream=_file)
            # TODO: insert values
            pass