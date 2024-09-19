"""plugin to show basic info"""
import papier
from papier.cli.commands import command


@command()
def showconf(args):
    """show the loaded configuration"""
    print(papier.config.dump())


@command()
def version(args):
    """show the installed version"""
    print(papier.__version__)
