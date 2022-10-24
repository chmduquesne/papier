import os
from papier.cli.commands import command, add_argument



@command(add_argument('path', help='path to import'), command_name='import')
def run(args):
    process(args.path)



def process(path):
    if os.path.isfile(path):
        print(path)
    elif os.path.isdir(path):
        for file in os.listdir(path):
            process(os.path.join(path, file))
    else:
        pass
