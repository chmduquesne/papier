import papier
from typing import NamedTuple, Self
import pypdf
import tempfile
import os
import shutil
import ocrmypdf


class Document(NamedTuple):
    pdfreader: pypdf.PdfReader
    text: str
    path: str
    tmpfile: str

    def __del__(self: Self) -> None:
        if self.tmpfile != '':
            if os.path.exists(self.tmpfile):
                os.remove(self.tmpfile)

    @classmethod
    def from_library(cls: Self, path: str) -> Self:
        """TODO Create a document from a library entry"""
        return None

    @classmethod
    def from_import(cls: Self, path: str) -> Self:
        """Create a Document from a file to import"""
        tmpfile = tempfile.NamedTemporaryFile(
                delete=False).name

        ocr = papier.config['import']['ocr'].get(str)
        match ocr:
            case 'never':
                shutil.copy(path, tmpfile)
            case 'always':
                ocrmypdf.ocr(path, tmpfile, redo_ocr=True, progress_bar=False)
            case 'empty':
                try:
                    ocrmypdf.ocr(path, tmpfile, progress_bar=False)
                except ocrmypdf.exceptions.PriorOcrFoundError:
                    shutil.copy(path, tmpfile)
            case _:
                raise ValueError('unexpected config value')

        pdfreader = pypdf.PdfReader(tmpfile)
        text = ''
        for p in pdfreader.pages:
            text += p.extract_text()
        return cls(pdfreader, text, path, tmpfile)
