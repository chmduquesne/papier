import pytest
import papier
from papier.cli.commands import command


def test_command_decorator() -> None:
    """test that we can register the command foo"""
    @command()
    def foo() -> None:
        pass


def test_command_decorator_fails() -> None:
    """test that if we register the command foo a second time, it fails"""
    with pytest.raises(papier.PluginError):
        @command()
        def foo() -> None:
            pass
