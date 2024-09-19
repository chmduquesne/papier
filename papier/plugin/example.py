"""example papier plugin"""
import papier.plugins
from papier.cli.commands import command, add_argument
from typing import List, Any


def on_plugins_loaded() -> None:
    print('all plugins loaded')


@command(add_argument('-f', '--flag', action='store_true'))
def example(args: List[Any]) -> None:
    """help for example command"""
    print(f'My arguments are {args}')


papier.plugins.register_listener('plugins loaded', on_plugins_loaded)
