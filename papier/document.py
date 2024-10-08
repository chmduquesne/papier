import papier
from typing import Self, List, Dict, Any
import pypdf
import tempfile
import os
import os.path
import shutil
import ocrmypdf
import hashlib
import re
from dataclasses import dataclass, field


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


@dataclass
class Document():
    path: str
    pdfreader: pypdf.PdfReader = field(default=None, init=False,
                                       repr=False)
    text: str = field(default="", init=False, repr=False)
    tmpfile: str = field(default="", init=False)
    sha256sum_: str = field(default="", init=False)

    def __del__(self: Self) -> None:
        """Clean-up after ourselves"""
        if self.tmpfile != '':
            if os.path.exists(self.tmpfile):
                os.remove(self.tmpfile)

    def sha256sum(self: Self) -> str:
        if self.sha256sum_ == '':
            with open(self.path, 'rb', buffering=0) as f:
                self.sha256sum_ = hashlib.file_digest(f, 'sha256').hexdigest()
        return self.sha256sum_

    @classmethod
    def from_library(cls: Self, path: str, sha256sum: str) -> Self:
        """TODO Create a document from a library entry"""
        res = cls.from_import(path)
        res.sha256sum_ = sha256sum
        return res

    @classmethod
    def from_import(cls: Self, path: str) -> Self:
        """Create a Document from a file to import"""
        res = cls(path)

        tmpfile = tempfile.NamedTemporaryFile(delete=False).name
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
                raise papier.ConfigError('ocr={ocr}: unexpected config value"')
        res.tmpfile = tmpfile

        res.pdfreader = pypdf.PdfReader(tmpfile)

        text = ''
        for p in res.pdfreader.pages:
            text += p.extract_text()
        res.text = normalized(text)

        return res

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
