import papier
from typing import NamedTuple, Self, List, Dict, Any
import pypdf
import tempfile
import os
import os.path
import shutil
import ocrmypdf
import hashlib
import re


def normalized(text: str) -> str:
    """Normalize text."""
    res = ''
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        # empty strings after stripping convert to newline character
        if not line:
            line = '\n'
        else:
            line = re.sub(r'\s+', ' ', line)
            # if the last character is not a letter or a number, add
            # newline character to a line
            if not re.search(r'[\w\d,\-]', line[-1]):
                line += '\n'
            else:
                line += ' '
        res += line
    res = res.strip()
    return res


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
        text = normalized(text)
        return cls(pdfreader, text, path, tmpfile, sha256sum)

    def _parts(self: Self, bold: bool = False, by_size: bool = False
               ) -> List[str]:
        """return parts of the documents"""
        parts = []

        def visit(text: str, cm: List[float], tm: List[float],
                  font_dict: Dict[str, Any], font_size: float) -> None:
            text = normalized(text)
            # We are only interested in non blank parts
            if text.strip() == '':
                return
            part = [text, font_size]
            if bold:
                if font_dict:
                    if '/BaseFont' in font_dict:
                        if 'bold' in font_dict['/BaseFont'].lower():
                            parts.append(part)
            else:
                parts.append(part)

        # If no subset of page numbers was provided, we visit all of them
        for page in self.pdfreader.pages:
            page.extract_text(visitor_text=visit)
        # Sort if necessary
        if by_size:
            parts.sort(key=lambda x: x[1], reverse=True)

        return [part[0] for part in parts]

    def important_parts(self: Self) -> List[str]:
        """return the important parts of the document"""
        important = self._parts(bold=True, by_size=True)
        if important == []:
            important = self._parts(by_size=True)
        return important

    def mtime(self: Self) -> float:
        return os.path.getmtime(self.path)
