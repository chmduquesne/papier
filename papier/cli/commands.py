import papier
import papier.plugins
import argparse
import argcomplete
import logging
import sys
from typing import Any, Callable, Tuple, List, Dict


papier.declare_event('subcommand_end',
                     'called after a subcommand finishes. Argument: '
                     '`command`, the name of the subcommand')


# Parser
cli = argparse.ArgumentParser(
    description='A pdf library organizer',
    epilog='Bug reports: https://github.com/chmduquesne/papier/issues'
)


# Global flags
cli.add_argument('--dry-run', action='store_true',
                 help='Run without making any modification',
                 default=False)
cli.add_argument('--progress', action=argparse.BooleanOptionalAction,
                 help='See progress bars',
                 default=True)
global_flags = ['dry_run', 'progress']


# Add the commands
subparsers = cli.add_subparsers(dest='command')


# Module where each command is defined
_command_module = dict()


# Inspired by https://mike.depalatis.net/blog/simplifying-argparse.html
def command(*added_arguments: Any, command_name: str = None) -> Callable:
    """Decorator to turn a function in a command

    Usage: @command(
                add_argument('x', help='x help'),
                add_argument('-b', help='foo help'),
                ...
                command_name='name'
                )

    The add_argument are passed to the subparser and should be interpreted as
    https://docs.python.org/3/library/argparse.html#the-add-argument-method

    If no command_name is given, it is inferred from the decorated
    function name
    """
    def decorator(func: Callable) -> None:
        name = command_name or func.__name__

        # Check if the command exists already
        if name in _command_module:
            raise papier.PluginError(
                    f'{name} is already defined by {_command_module[name]}'
                    )
        _command_module[name] = func.__module__

        parser = subparsers.add_parser(name,
                                       description=func.__doc__,
                                       help=func.__doc__)
        for args, kwds in added_arguments:
            # Hack to pass a argcomplete.completer:
            #
            # argcomplete expects a completer to be passed by attributing
            # the result of parser.add_argument(). See
            # https://kislyuk.github.io/argcomplete/#specifying-completers
            #
            # Because we use a decorator here, we cannot do that
            # with our auxiliary add_argument function. Instead, the user
            # of this function is expected to pass the completer as a
            # keyword argument named 'completer'.
            #
            # The code below removes this completer keyword that
            # parser.add_argument does not expect, and assigns it the way
            # argcomplete expects it.
            keyword_args = kwds
            completer = None
            if 'completer' in keyword_args:
                completer = keyword_args['completer']
                del keyword_args['completer']
            parser.add_argument(*args, **keyword_args).completer = completer
        parser.set_defaults(func=func)
    return decorator


# When passed to the decorator, adds argments to the subparser
def add_argument(*names_or_flags: Any, **kwds: Any
                 ) -> Tuple[List[Any], Dict[str, Any]]:
    """Adds argument to the subparser. If the keyword 'completer' is
    passed, a completer compatible with argcomplete.completers is
    expected
    """
    return names_or_flags, kwds


# Main entry point
def main() -> None:
    # Start logging before we even parse the command line
    logfile = papier.config['log'].as_str()
    if logfile != "-":
        logging.basicConfig(
                filename=logfile, encoding='utf-8', level=logging.DEBUG
        )
    else:
        logging.basicConfig(
                stream=sys.stdout, encoding='utf-8', level=logging.DEBUG
        )
    logging.captureWarnings(True)

    # Load the plugins so that we know what commands must be parsed
    # Core plugins first, user-specified second to avoid collisions
    papier.plugins.load_plugins(papier.core_plugins)
    papier.plugins.load_plugins(papier.config['plugins'].as_str_seq())

    # Enable command line completion
    argcomplete.autocomplete(cli)

    # Parse the command line
    args = cli.parse_args()

    # Move the global flags into the config
    for (key, value) in vars(args).items():
        if key in global_flags:
            papier.config[key].set(value)
    for key in global_flags:
        if key in args:
            delattr(args, key)

    if args.command is None:
        cli.print_help()
    else:
        # TODO: find a way to list all events
        args.func(args)
        papier.send_event('subcommand_end')
