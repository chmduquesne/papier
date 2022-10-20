"""plugin to show basic info"""
import papier
import confuse
from papier.cli.commands import command, add_argument


@command()
def showconf():
    """show the loaded configuration"""
    print(papier.config.dump())


@command()
def version():
    """show the installed version"""
    print(papier.__version__)
