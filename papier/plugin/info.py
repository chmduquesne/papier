"""plugin to show basic info"""
import papier
from papier.cli.commands import command
from typing import List, Any


@command()
def showconf(args: List[Any, ...]) -> None:
    """show the loaded configuration"""
    print(papier.config.dump())


@command()
def version(args: List[Any, ...]) -> None:
    """show the installed version"""
    print(papier.__version__)
