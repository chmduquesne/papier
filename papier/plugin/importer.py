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




@command(
        add_argument('path', help='path to import'),
        add_argument('--copy', action=argparse.BooleanOptionalAction,
            help=f'Copy files to the library directory after import',
            default=argparse.SUPPRESS),
        add_argument('--move', action=argparse.BooleanOptionalAction,
            help=f'Move files to the library directory after import',
            default=argparse.SUPPRESS),
        add_argument('--write', action=argparse.BooleanOptionalAction,
            help=f'Write tags to the files copied/moved to the library after import',
            default=argparse.SUPPRESS),
        add_argument('--ocr', action=argparse.BooleanOptionalAction,
            help=f'Run OCR on files prior to import if no text is embedded',
            default=argparse.SUPPRESS),
        add_argument('--redo-ocr', action=argparse.BooleanOptionalAction,
            help=f'Run OCR on files prior to import in any case',
            default=argparse.SUPPRESS),
        add_argument('--tag', action='append',
            help=f'Set the given tag to the given value',
            default=argparse.SUPPRESS),
        add_argument('--autotag', action=argparse.BooleanOptionalAction,
            help=f'Automatically tag the files',
            default=argparse.SUPPRESS),
        command_name='import')
def run(args):
    papier.config['import'].set_args(args)
    for p in find_pdfs(args.path):
        process(p)
