import papier
from typing import NamedTuple, Self
import pypdf
import tempfile
import os
import shutil
import ocrmypdf
import hashlib


class Document(NamedTuple):
    pdfreader: pypdf.PdfReader
    text: str
    path: str
    tmpfile: str
    sha256sum: str

    def __del__(self: Self) -> None:
        """Clean-up after ourselves"""
        if self.tmpfile != '':
            if os.path.exists(self.tmpfile):
                os.remove(self.tmpfile)

    def __repr__(self: Self) -> str:
        """For debugging purposes"""
        return (f'Document(path={self.path}, '
                f'tmpfile={self.tmpfile}, '
                f'sha256sum={self.sha256sum})')

    @classmethod
    def from_library(cls: Self, path: str) -> Self:
        """TODO Create a document from a library entry"""
        return None

    @classmethod
    def from_import(cls: Self, path: str) -> Self:
        """Create a Document from a file to import"""
        with open(path, 'rb', buffering=0) as f:
            sha256sum = hashlib.file_digest(f, 'sha256').hexdigest()

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
        return cls(pdfreader, text, path, tmpfile, sha256sum)
