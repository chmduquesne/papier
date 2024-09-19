"""plugin to show basic info"""
import papier
from papier.cli.commands import command
from typing import List


@command()
def showconf(args: List[...]) -> None:
    """show the loaded configuration"""
    print(papier.config.dump())


@command()
def version(args: List[...]) -> None:
    """show the installed version"""
    print(papier.__version__)
