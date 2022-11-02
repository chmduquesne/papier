import os
import re
import argparse
from papier.cli.commands import command, add_argument
import papier
from tempfile import NamedTemporaryFile
import logging
import ocrmypdf
from PyPDF2 import PdfReader, PdfWriter



log = logging.getLogger(__name__)



PDF = re.compile(r'.*\.pdf', re.IGNORECASE)



def find_pdfs(path):
    if os.path.isfile(path):
        if PDF.match(path):
            yield path
    elif os.path.isdir(path):
        for p in os.listdir(path):
            yield from find_pdfs(os.path.join(path,p))



def process(path):
    meta = {k: v.get() for k, v in papier.config['import']['set_tag'].items()}
    print(meta)

    #path = ocr(path)
    path = tag(path)
    print(path)



def tag(path, tags={"/Author": "Christophe-Marie Duquesne"}):
    with NamedTemporaryFile(dir='.', delete=False) as tmp:
        reader = PdfReader(path)

        writer = PdfWriter()
        writer.appendPagesFromReader(reader)
        writer.addMetadata(reader.getDocumentInfo())

        # Add the metadata
        writer.add_metadata(tags)
        writer.write(tmp)
        return tmp.name




def ocr(path):
    if papier.config["import"]["ocr"].get():
        try:
            with NamedTemporaryFile() as tmp:
                ocrmypdf.ocr(path, tmp.name,
                        redo_ocr=papier.config["import"]["redo_ocr"].get())
                return tmp.name
        except ocrmypdf.exceptions.PriorOcrFoundError:
            pass
    return path



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
