from argparse import ArgumentParser


# Parser
cli = ArgumentParser(
    description='A pdf library organizer',
    epilog='Bug reports: https://github.com/chmduquesne/papier/issues'
)
cli.add_argument("-d", "--dry-run", action="store_true",
    help="Run without making any modification")



# Add the subcommands
subparsers = cli.add_subparsers(
        dest="subcommand",
        description="available subcommands"
        help="action to take on your pdf library"
        )


# Inspired by https://mike.depalatis.net/blog/simplifying-argparse.html
def subcommand(*added_arguments, parent=subparsers):
    def decorator(func):
        name = func.__name__

        # remove leading _ in the name
        if name.startswith("_"):
            name = name[1:]

        parser = parent.add_parser(name, description=func.__doc__)
        for args, kwargs in added_arguments:
            parser.add_argument(*args, **kwargs)
        parser.set_defaults(func=func)
    return decorator


# When passed to the decorator, adds argments to the subparser
def add_argument(*names_or_flags, **kwargs):
    return names_or_flags, kwargs




@subcommand(add_argument('path', help="path to import"))
def _import(args):
    """
    import the given path
    """
    if args.pretend:
        print("just pretending!")
    print(f"importing {args.path} into your library")


@subcommand()
def write(args):
    """
    Write changes in the library to the files
    """
    print(f"writing changes from your library to the files")


@subcommand()
def contribute(args):
    """
    Contribute data to improve papier
    """
    print(f"writing changes from your library to the files")


def main():
    args = cli.parse_args()
    if args.subcommand is None:
        cli.print_help()
    else:
        args.func(args)
