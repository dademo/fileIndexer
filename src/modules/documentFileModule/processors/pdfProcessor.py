import logging
import datetime
import re
from typing import List, Tuple, Callable, Any

from public import FileDescriptor, ConfigHandler
from modules.documentFileModule import DocumentFileProcessor, DbQuerier

from PyPDF2 import PdfFileReader
from PyPDF2.utils import PdfReadError, PdfReadWarning
import sqlalchemy

logger = logging.getLogger('fileIndexer').getChild('modules.documentFileModule.processors.PdfProcessor')


class PdfProcessor(DocumentFileProcessor):

    dateFormat = "D:%Y%m%d%H%M%S"
    tzFormatRe = re.compile(r"(?P<globalFormat>(?P<offsetRelation>\+|\-)(?P<offsetHours>[0-9]{2}')(?P<offsetMinutes>[0-9]{2}')|Z)")
    noTextRe = re.compile(r"^[\W_]*$")

    def formatDate(self, dateStr: str) -> datetime.datetime:
        try:
            date = datetime.datetime.strptime(dateStr[:16], self.dateFormat)
        except ValueError as ex:
            # Not a valid format
            logger.warning('Unable to parse date string [%s] (%s)' % (dateStr, ex))
            return None

        dateTzReRes = self.tzFormatRe.search(dateStr[17:])
        if dateTzReRes:
            tzResDict = dateTzReRes.groupdict()
            if tzResDict['globalFormat'] == 'Z':
                date.replace(tzinfo=datetime.timezone.utc)
            else:
                date.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=int(tzResDict['offsetHours']), minutes=int(tzResDict['offsetMinutes']))))
        return date

    # from: https://www.oreilly.com/library/view/pdf-explained/9781449321581/ch04.html#dates
    # pdf date format: (D:YYYYMMDDHHmmSSOHH'mm')
    def mapDocumentInfos(self, pdfDocumentInfo: dict) -> dict:
        # Mapping defs
        mapFcts = [
            # Deletting the first '/'
            lambda k, v: (k[1:] if k[0] == '/' else k, v),
            lambda k, v: (k[0].lower() + k[1:], v),
            lambda k, v: (k, self.formatDate(v) if any(map(lambda _k: k == _k, ['creationDate', 'modDate'])) else v)
        ]
        def apply_mappings(dictValues: Tuple[str, Any], mappings: List[Callable[[str, Any], Any]]):
            finalValue = dictValues
            for mapFct in mappings:
                finalValue = mapFct(*finalValue)
            return finalValue

        return dict(
            map(
                lambda item: apply_mappings(item, mapFcts),
                pdfDocumentInfo.items()
            )
        )

    def getDocumentWordAndCharacterCount(self, pdfDocument: PdfFileReader) -> Tuple[int, int]:
        wordCount = 0
        characterCount = 0

        for pageNum in range(pdfDocument.getNumPages()):
            characterCountList = list(map(
                lambda w: len(w),
                filter(
                    lambda w: not self.noTextRe.match(w),
                    re.compile(r'\s+').split(pdfDocument.getPage(pageNum).extractText())
            )))
            wordCount += len(characterCountList)
            characterCount += sum(characterCountList)
        return wordCount, characterCount


    def saveDocumentInfos(self, pdfDocument: PdfFileReader, fileDescriptor: FileDescriptor, dbQuerier: DbQuerier) -> None:

        documentMetas = self.mapDocumentInfos(pdfDocument.getDocumentInfo())

        def getMeta(key: str) -> Any:
            if key in documentMetas:
                return documentMetas[key]
            else:
                return None

        # Saving document
        documentWordCount, documentCharacterCount = self.getDocumentWordAndCharacterCount(pdfDocument)
        documentEntity = dbQuerier.getFileDocumentEntity(
            fileDescriptor=fileDescriptor,
            title=getMeta('title'),
            author=getMeta('author'),
            pageCount=pdfDocument.getNumPages(),
            wordCount=documentWordCount,
            characterCount=documentCharacterCount
        )

        # Saving document chapters, TODO

        # Saving document metas
        for documentMetaName, documentMetaValue in documentMetas.items():
            metaNameEntity = dbQuerier.getMetaNameEntity(documentMetaName)

            if isinstance(documentMetaValue, list) or isinstance(documentMetaValue, set):
                for _documentMetaValue in documentMetaValue:
                    dbQuerier.getMetaValueEntity(documentEntity, metaNameEntity, _documentMetaValue)
            else:
                    dbQuerier.getMetaValueEntity(documentEntity, metaNameEntity, documentMetaValue)


    def process(self, documentFileModule: 'DocumentFileModule', fileDescriptor: FileDescriptor, appConfig: ConfigHandler, dbEngine: sqlalchemy.engine.Engine):

        querier = documentFileModule.getDBQuerier(dbEngine, appConfig)

        with fileDescriptor.open() as _file:
            pdfDocument = PdfFileReader(stream=_file)
            try: 
                # Trying to decrypt with an empty password
                if pdfDocument.isEncrypted:
                    pdfDocument.decrypt('')

                self.saveDocumentInfos(pdfDocument, fileDescriptor, querier)
            except (PdfReadError, PdfReadWarning) as ex:
                # Can't decrypt the pdf file
                logger.warning('Unable to decrypt file [%s] (%s)' % (fileDescriptor.fullPath, ex))
                return