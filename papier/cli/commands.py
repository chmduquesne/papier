from argparse import ArgumentParser


cli = ArgumentParser(
    description="A pdf library organizer",
    epilog="Please report bugs to https://github.com/chmduquesne/papier/issues"
)
cli.add_argument("-d", "--dry-run", action="store_true",
    help="Run without making any modification")


subparsers = cli.add_subparsers(dest="subcommand")


def argument(*names_or_flags, **kwargs):
    return names_or_flags, kwargs


def subcommand(*subparser_args, parent=subparsers):
    def decorator(func):
        if not func.__name__.startswith("subcommand_"):
            raise NameError("subcommands function names need to start with 'subcommand_'")
        name = func.__name__[len('subcommand_'):]
        parser = parent.add_parser(name, description=func.__doc__)
        for args, kwargs in subparser_args:
            parser.add_argument(*args, **kwargs)
        parser.set_defaults(func=func)
    return decorator


@subcommand(argument('path', help="path to import"))
def subcommand_import(args):
    """
    import the given path
    """
    if args.pretend:
        print("just pretending!")
    print(f"importing {args.path} into your library")


@subcommand()
def subcommand_write(args):
    """
    Write changes in the library to the files
    """
    print(f"writing changes from your library to the files")


def main():
    args = cli.parse_args()
    if args.subcommand is None:
        cli.print_help()
    else:
        args.func(args)
