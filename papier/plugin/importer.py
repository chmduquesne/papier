import os
import re
from papier.cli.commands import command, add_argument



PDF = re.compile(r'.*\.pdf', re.IGNORECASE)



def find_pdfs(path):
    if os.path.isfile(path):
        if PDF.match(path):
            yield path
    elif os.path.isdir(path):
        for p in os.listdir(path):
            yield from find_pdfs(os.path.join(path,p))



def process(path):
    print(path)



@command(add_argument('path', help='path to import'), command_name='import')
def run(args):
    for p in find_pdfs(args.path):
        process(p)
