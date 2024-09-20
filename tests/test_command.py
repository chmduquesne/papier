import pytest
from papier.cli.commands import command



def test_command_decorator():
    """test that we can register the command foo"""
    @command()
    def foo():
        pass


def test_command_decorator_fails():
    """test that if we register the command foo a second time, it fails"""
    with pytest.raises(NameError):
        @command()
        def foo():
            pass
