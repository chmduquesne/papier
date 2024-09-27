"""importing into papier"""

import os
import re
import argparse
from papier.cli.commands import command, add_argument
import papier
import papier.library
from tempfile import NamedTemporaryFile as TempFile
import logging
from pypdf import PdfReader, PdfWriter
from argcomplete.completers import FilesCompleter
from typing import Generator, Dict, List, Any


# Logger for this plugin
log = logging.getLogger(__name__)


# Which files we process
PDF = re.compile(r'.*\.pdf', re.IGNORECASE)


def find_pdfs(path: str) -> Generator[str, str, str]:
    """returns all the pdfs under a given path"""
    if os.path.isfile(path):
        if PDF.match(path):
            yield path
    elif os.path.isdir(path):
        for p in os.listdir(path):
            yield from find_pdfs(os.path.join(path, p))


def get_conf() -> str:
    """returns the import config"""
    params = {
        'copy': bool,
        'delete': bool,
        'modify': bool,
        'ocr': str,
        'redo_ocr': bool,
        'autotag': bool,
        'set_tag': dict
        }
    return papier.config['import'].get(params)


def process(path: str) -> None:
    log.info(f'processing {path}')
    doc = papier.Document.from_import(path)

    if papier.library.has(doc):
        log.info(f'skipping {path}')
        return

    tags = dict()
    for e in papier.extractors:
        print(e)
        extracted = e.extract(doc, tags)
        print(extracted)
        tags |= extracted
    papier.library.add(doc)


def autotag(path: str, set_tags: Dict[str, str] = None) -> Dict[str, str]:
    return {}


def tag(path: str,
        tags: dict[str, str] = {"/Author": "Christophe-Marie Duquesne"}
        ) -> str:
    with TempFile(dir='.', delete=False) as tmp:
        reader = PdfReader(path)

        writer = PdfWriter()
        writer.appendPagesFromReader(reader)
        writer.addMetadata(reader.getDocumentInfo())

        # Add the metadata
        writer.add_metadata(tags)
        writer.write(tmp)
        return tmp.name


def split_pair(tag_pair: str) -> tuple[str, ...]:
    """splits the input string at the first equals sign"""
    i = tag_pair.find('=')
    if i == -1:
        raise argparse.ArgumentError(
                'Wrong argument for --set-tag: expected <key>=<value>')
    return (tag_pair[:i], tag_pair[i+1:])


@command(
        add_argument('path', help='path to import',
                     completer=FilesCompleter(allowednames=('.pdf'))),
        add_argument('--copy', action=argparse.BooleanOptionalAction,
                     help='Copy files to the library directory after import',
                     default=argparse.SUPPRESS),
        add_argument('--delete', action=argparse.BooleanOptionalAction,
                     help='Delete files that were succesfully imported',
                     default=argparse.SUPPRESS),
        add_argument('--overwrite-text', action=argparse.BooleanOptionalAction,
                     help='Rewrite the files copied to the library',
                     default=argparse.SUPPRESS),
        add_argument('--overwrite-tags', action=argparse.BooleanOptionalAction,
                     help='Rewrite the files copied to the library',
                     default=argparse.SUPPRESS),
        add_argument('--ocr', action=argparse.BooleanOptionalAction,
                     help='Run OCR prior to import if no text is embedded',
                     choices=['always', 'never', 'empty'],
                     default=argparse.SUPPRESS),
        add_argument('--set-tag', action='append',
                     help='Set the given tag to the given value',
                     default=argparse.SUPPRESS),
        add_argument('--autotag', action=argparse.BooleanOptionalAction,
                     help='Automatically tag the files',
                     default=argparse.SUPPRESS),
        command_name='import')
def run(args: List[Any]) -> None:
    if hasattr(args, 'set_tag'):
        for tag_pair in args.set_tag:
            tag_key, tag_value = split_pair(tag_pair)
            papier.config['import']['set_tag'][tag_key].set(tag_value)
        del args.__dict__['set_tag']

    papier.config['import'].set_args(args)
    for p in find_pdfs(args.path):
        process(p)
