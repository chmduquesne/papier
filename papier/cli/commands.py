from argparse import ArgumentParser
import confuse


# Parser
cli = ArgumentParser(
    description='A pdf library organizer',
    epilog='Bug reports: https://github.com/chmduquesne/papier/issues'
)
cli.add_argument("-d", "--dry-run", action="store_true",
    help="Run without making any modification")



# Add the commands
subparsers = cli.add_subparsers(
        dest="command",
        description="available commands",
        help=""
        )


# Existing commands
existing_subcommands = set()


# Inspired by https://mike.depalatis.net/blog/simplifying-argparse.html
def command(*added_arguments, subcommand_name=None):
    def decorator(func):
        name = subcommand_name or func.__name__

        if name in existing_subcommands:
            raise NameError(f"{name} is already an existing command")
        existing_subcommands.add(name)

        parser = subparsers.add_parser(name, description=func.__doc__)
        for args, kwargs in added_arguments:
            parser.add_argument(*args, **kwargs)
        parser.set_defaults(func=func)
    return decorator


# When passed to the decorator, adds argments to the subparser
def add_argument(*names_or_flags, **kwargs):
    return names_or_flags, kwargs




@command(add_argument('path', help="path to import"), subcommand_name='import')
def _import(args):
    """
    import the given path
    """
    if args.pretend:
        print("just pretending!")
    print(f"importing {args.path} into your library")


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
