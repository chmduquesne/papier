import papier
import papier.cli
from unittest.mock import patch
import sys
import pytest


def test_version(capsys: pytest.CaptureFixture) -> None:
    argv = ['papiers', 'version']
    with patch.object(sys, 'argv', argv):
        papier.cli.main()
        out, err = capsys.readouterr()
        assert out.strip() == papier.__version__
