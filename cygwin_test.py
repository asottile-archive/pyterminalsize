import pipes
import subprocess
import sys

from pyterminalsize_test import _run
from pyterminalsize_test import _test_file
from pyterminalsize_test import GET_TERMINAL_SIZE_PROG


def test_cygwin():
    with _test_file(GET_TERMINAL_SIZE_PROG) as path:
        out, _ = _run(
            (
                'bash', '-c',
                ' '.join(pipes.quote(part) for part in (
                    sys.executable, '-m', 'coverage', 'run', path,
                ))
            ),
            stdout=subprocess.PIPE,
        )
    assert "source='tput'" in out
