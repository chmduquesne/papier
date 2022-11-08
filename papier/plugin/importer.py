import os
import re
import argparse
from papier.cli.commands import command, add_argument
import papier
from tempfile import NamedTemporaryFile as TempFile
import logging
import ocrmypdf
from PyPDF2 import PdfReader, PdfWriter
import shutil
import confuse



log = logging.getLogger(__name__)



PDF = re.compile(r'.*\.pdf', re.IGNORECASE)
CONFIG_TEMPLATE = {
        'copy': bool,
        'delete': bool,
        'modify': bool,
        'ocr': bool,
        'redo_ocr': bool,
        'autotag': bool,
        'set_tag': dict
        }



def find_pdfs(path):
    if os.path.isfile(path):
        if PDF.match(path):
            yield path
    elif os.path.isdir(path):
        for p in os.listdir(path):
            yield from find_pdfs(os.path.join(path,p))




def process(path):
    cfg = papier.config['import'].get(CONFIG_TEMPLATE)
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
    try:
        ocrmypdf.ocr(src, dst, redo_ocr=redo_ocr, progress_bar=False)
    except ocrmypdf.exceptions.PriorOcrFoundError:
        pass



def split_pair(tag_pair):
    """splits the tag pair at the first equals sign"""
    i = tag_pair.find('=')
    if i == -1:
        raise argparse.ArgumentError('Wrong argument for --set-tag: expected <key>=<value>')
    return (tag_pair[:i], tag_pair[i+1:])



@command(
        add_argument('path', help='path to import'),
        add_argument('--copy', action=argparse.BooleanOptionalAction,
            help=f'Copy files to the library directory after import',
            default=argparse.SUPPRESS),
        add_argument('--delete', action=argparse.BooleanOptionalAction,
            help=f'Delete original files after copy',
            default=argparse.SUPPRESS),
        add_argument('--modify', action=argparse.BooleanOptionalAction,
            help=f'Rewrite the files copied to the library after import to include tags/ocr',
            default=argparse.SUPPRESS),
        add_argument('--ocr', action=argparse.BooleanOptionalAction,
            help=f'Run OCR on files prior to import if no text is embedded',
            default=argparse.SUPPRESS),
        add_argument('--redo-ocr', action=argparse.BooleanOptionalAction,
            help=f'Run OCR on files prior to import in any case',
            default=argparse.SUPPRESS),
        add_argument('--set-tag', action='append',
            help=f'Set the given tag to the given value',
            default=argparse.SUPPRESS),
        add_argument('--autotag', action=argparse.BooleanOptionalAction,
            help=f'Automatically tag the files',
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
