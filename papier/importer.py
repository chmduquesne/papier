import os
from papier import config



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
