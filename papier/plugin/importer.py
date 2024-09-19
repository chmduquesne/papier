"""importing into papier"""

import os
import re
import argparse
from papier.cli.commands import command, add_argument
import papier
from tempfile import NamedTemporaryFile as TempFile
import logging
import ocrmypdf
from pypdf import PdfReader, PdfWriter
import shutil
from argcomplete.completers import FilesCompleter


# Logger for this plugin
log = logging.getLogger(__name__)


# Which files we process
PDF = re.compile(r'.*\.pdf', re.IGNORECASE)


def find_pdfs(path):
    """returns all the pdfs under a given path"""
    if os.path.isfile(path):
        if PDF.match(path):
            yield path
    elif os.path.isdir(path):
        for p in os.listdir(path):
            yield from find_pdfs(os.path.join(path, p))


def get_conf():
    """returns the import config"""
    params = {
        'copy': bool,
        'delete': bool,
        'modify': bool,
        'ocr': bool,
        'redo_ocr': bool,
        'autotag': bool,
        'set_tag': dict
        }
    return papier.config['import'].get(params)


def process(path):
    log.info(f'processing {path}')
    cfg = get_conf()
    src = path
    with TempFile() as tmp:
        dst = tmp.name

        # copy the file to dst, run ocr if necessary
        shutil.copy(src, dst)
        if cfg.ocr:
            ocr(src, dst, redo_ocr=cfg.redo_ocr)
        metadata = {}
        set_tags = {k: v for k, v in cfg.set_tag.items()}
        if cfg.autotag:
            # autotag should be interactive and return a status
            metadata |= autotag(dst, set_tags=set_tags)
        if cfg.modify:
            pass
        if cfg.copy:
            pass


def autotag(path, set_tags=None):
    return {}


def tag(path, tags={"/Author": "Christophe-Marie Duquesne"}):
    with TempFile(dir='.', delete=False) as tmp:
        reader = PdfReader(path)

        writer = PdfWriter()
        writer.appendPagesFromReader(reader)
        writer.addMetadata(reader.getDocumentInfo())

        # Add the metadata
        writer.add_metadata(tags)
        writer.write(tmp)
        return tmp.name


def ocr(src, dst, redo_ocr=False):
    """runs ocr on the imput file"""
    try:
        ocrmypdf.ocr(src, dst, redo_ocr=redo_ocr, progress_bar=False)
    except ocrmypdf.exceptions.PriorOcrFoundError:
        pass


def split_pair(tag_pair):
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
                     help='Delete original files after copy',
                     default=argparse.SUPPRESS),
        add_argument('--modify', action=argparse.BooleanOptionalAction,
                     help='Rewrite the files copied to the library',
                     default=argparse.SUPPRESS),
        add_argument('--ocr', action=argparse.BooleanOptionalAction,
                     help='Run OCR prior to import if no text is embedded',
                     default=argparse.SUPPRESS),
        add_argument('--redo-ocr', action=argparse.BooleanOptionalAction,
                     help='Run OCR on files prior to import in any case',
                     default=argparse.SUPPRESS),
        add_argument('--set-tag', action='append',
                     help='Set the given tag to the given value',
                     default=argparse.SUPPRESS),
        add_argument('--autotag', action=argparse.BooleanOptionalAction,
                     help='Automatically tag the files',
                     default=argparse.SUPPRESS),
        command_name='import')
def run(args):
    if hasattr(args, 'set_tag'):
        for tag_pair in args.set_tag:
            tag_key, tag_value = split_pair(tag_pair)
            papier.config['import']['set_tag'][tag_key].set(tag_value)
        del args.__dict__['set_tag']

    papier.config['import'].set_args(args)
    for p in find_pdfs(args.path):
        process(p)
