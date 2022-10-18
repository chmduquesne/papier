import os
from papier import config


def run():
    process(config["import"]["path"].as_filename())


def process(path):
    if os.path.isfile(path):
        print(path)
    elif os.path.isdir(path):
        for file in os.listdir(path):
            process(os.path.join(path, file))
    else:
        pass
