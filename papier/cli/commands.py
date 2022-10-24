import papier
import papier.plugins
import argparse


# Parser
cli = argparse.ArgumentParser(
    description='A pdf library organizer',
    epilog='Bug reports: https://github.com/chmduquesne/papier/issues'
)
cli.add_argument('-p', '--pretend', action='store_true',
    help='Run without making any modification')


# Add the commands
subparsers = cli.add_subparsers(dest='command')


# Existing commands
_existing_commands = set()


# Inspired by https://mike.depalatis.net/blog/simplifying-argparse.html
def command(*added_arguments, command_name=None):
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
    def decorator(func):
        name = command_name or func.__name__

        if name in _existing_commands:
            raise NameError(f'{name} is already an existing command')
        _existing_commands.add(name)

        parser = subparsers.add_parser(name, description=func.__doc__,
                help=func.__doc__)
        for args, kwds in added_arguments:
            parser.add_argument(*args, **kwds)
        parser.set_defaults(func=func)
    return decorator


# When passed to the decorator, adds argments to the subparser
def add_argument(*names_or_flags, **kwds):
    return names_or_flags, kwds


# Main entry point
def main():
    # Load the core plugins first, then the user plugins (to avoid command
    # collisions)
    papier.plugins.load_plugins(papier.default_plugins)
    papier.plugins.load_plugins(papier.config['plugins'].as_str_seq())

    args = cli.parse_args()
    if args.command is None:
        cli.print_help()
    else:
        papier.plugins.send("command starting", command=args.command)
        args.func(args)
        papier.plugins.send("command finished", command=args.command)
