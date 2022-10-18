from argparse import ArgumentParser
import confuse


# Parser
cli = ArgumentParser(
    description='A pdf library organizer',
    epilog='Bug reports: https://github.com/chmduquesne/papier/issues'
)
cli.add_argument("-p", "--pretend", action="store_true",
    help="Run without making any modification")



# Add the commands
subparsers = cli.add_subparsers(dest="command")


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
            raise NameError(f"{name} is already an existing command")
        _existing_commands.add(name)

        parser = subparsers.add_parser(name, description=func.__doc__,
                help=func.__doc__)
        for args, kwargs in added_arguments:
            parser.add_argument(*args, **kwargs)
        parser.set_defaults(func=func)
    return decorator


# When passed to the decorator, adds argments to the subparser
def add_argument(*names_or_flags, **kwargs):
    return names_or_flags, kwargs




@command(add_argument('path', help="path to import"), command_name='import')
def func_import(args):
    """
    import the given path
    """
    if args.pretend:
        print("just pretending!")
    from papier import importer
    importer.run(args)



@command()
def write(args):
    """
    Write changes in the library to the files
    """
    print(args)
    print(f"writing changes from your library to the files")


@command()
def contribute(args):
    """
    Contribute data to improve papier
    """
    print(f"writing changes from your library to the files")


def main():
    config = confuse.Configuration('papier', 'papier')
    args = cli.parse_args()
    if args.command is None:
        cli.print_help()
    else:
        args.func(args)
