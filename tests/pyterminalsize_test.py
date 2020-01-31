from __future__ import unicode_literals

import collections
import os
import subprocess
import sys

import _pyterminalsize
import pytest

import pyterminalsize


PY3 = str is not bytes
WIN = sys.platform == 'win32'


def to_n(s):
    if isinstance(s, bytes) and PY3:  # pragma: no cover (py3)
        s = s.decode('UTF-8')
    elif not isinstance(s, bytes) and not PY3:  # pragma: no cover (py2)
        s = s.encode('UTF-8')
    return s


def dct_to_native(dct):
    return dict((to_n(k), to_n(v)) for k, v in dct.items())


@pytest.fixture(autouse=True, scope='session')
def reset_terminal_size():
    size = pyterminalsize.get_terminal_size()
    yield
    for fd in (0, 1, 2):
        try:
            _pyterminalsize.set_terminal_size(fd, *size[:2])
        except OSError:  # pragma: no cover (windows)
            if fd != 0:
                raise


def norm(s):
    return s.replace('\r\n', '\n')


def _run(cmd, **kwargs):
    stdin = kwargs.pop('stdin', None)
    if stdin is not None:
        kwargs['stdin'] = subprocess.PIPE
    if 'env' in kwargs:
        # Allows `random` to be importable
        kwargs['env']['SYSTEMROOT'] = os.environ.get('SYSTEMROOT', '')
        if 'PATH' not in kwargs['env']:
            kwargs['env']['PATH'] = os.environ['PATH']
        kwargs['env'] = dct_to_native(kwargs['env'])
    proc = subprocess.Popen(cmd, **kwargs)
    out, err = proc.communicate(stdin)
    assert not proc.returncode, (proc.returncode, out, err)
    return (
        norm(out.decode('UTF-8')) if out is not None else None,
        norm(err.decode('UTF-8')) if err is not None else None,
    )


def run_with_coverage(*args, **kwargs):
    return _run((sys.executable, '-m', 'coverage', 'run') + args, **kwargs)


def test_from_tput_no_tput_on_path():
    out, _ = run_with_coverage(
        '-m', 'testing.from_tput_prog',
        stdout=subprocess.PIPE, env={'PATH': '', 'TERM': 'dumb'},
    )
    key = collections.namedtuple('key', ('win', 'py3'))
    error = {
        key(win=True, py3=True): (
            '[WinError 2] The system cannot find the file specified'
        ),
        key(win=True, py3=False): (
            '[Error 2] The system cannot find the file specified'
        ),
        key(win=False, py3=True): (
            "[Errno 2] No such file or directory: 'tput': 'tput'"
        ),
        key(win=False, py3=False): (
            '[Errno 2] No such file or directory'
        ),
    }
    assert out == (
        'Caught OSError\n'
        '{}\n'.format(error[key(win=WIN, py3=PY3)])
    )


def test_from_tput_bs_terminal_proc_returncode():
    out, _ = run_with_coverage(
        '-m', 'testing.from_tput_prog',
        stdout=subprocess.PIPE, env={'TERM': 'bs'},
    )
    assert out == (
        'Caught OSError\n'
        'tput returned 3\n'
    )


def test_from_tput_no_term():
    out, _ = run_with_coverage(
        '-m', 'testing.from_tput_prog',
        stdout=subprocess.PIPE, env={},
    )
    assert out == (
        'Caught OSError\n'
        'Cannot determine cols / lines without TERM\n'
    )


def test_from_tput_dumb_term():
    out, _ = run_with_coverage(
        '-m', 'testing.from_tput_prog',
        # Both being a pipe is important, this makes tput lookup based on TERM
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={'TERM': 'dumb'},
    )
    assert out == '(80, 24)\n'


def test_from_environment():
    out, _ = run_with_coverage(
        '-m', 'testing.get_terminal_size_prog',
        stdout=subprocess.PIPE,
        env={'COLUMNS': '10', 'LINES': '20'},
    )
    assert out == "Size(columns=10, lines=20, source='environment')\n"


def test_get_from_tput():
    out, _ = run_with_coverage(
        '-m', 'testing.get_terminal_size_prog',
        # when stdin / stdout / stderr are all pipes it will fall back to tput
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=b'',
        env={'TERM': 'dumb'},
    )
    assert out == "Size(columns=80, lines=24, source='tput')\n"


def test_fallback():
    out, _ = run_with_coverage(
        '-m', 'testing.get_terminal_size_prog',
        # when stdin / stdout / stderr are all pipes it will fall back to tput
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=b'',
        # When TERM is not set it cannot fall back to tput
        env={},
    )
    assert out == "Size(columns=10, lines=20, source='fallback')\n"


@pytest.mark.parametrize('source', ('stdout', 'stderr'))
def test_from_source(source):
    kwargs = {
        'stdin': b'',
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
    }
    kwargs.pop(source)
    arg = 'stderr' if source == 'stdout' else 'stdout'
    out, err = run_with_coverage(
        '-m', 'testing.changes_size_prog', arg, **kwargs
    )
    output = err if source == 'stdout' else out
    assert output == (
        "Size(columns=30, lines=40, source='{0}')".format(source)
    )


@pytest.mark.xfail(
    sys.platform == 'win32',
    reason='stdin does not work correctly on windows'
)
def test_from_stdin():
    test_from_source('stdin')
