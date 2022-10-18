"""example papier plugin"""
import papier.plugins
from papier.cli.commands import command, add_argument


def on_plugins_loaded():
    print('all plugins loaded')


@command(add_argument('-f', '--flag', action='store_true'))
def example(args):
    """help for example command"""
    print(f'My arguments are {args}')


papier.plugins.register_listener('plugins loaded', on_plugins_loaded)
