[![Build Status](https://travis-ci.org/asottile/pyterminalsize.svg?branch=master)](https://travis-ci.org/asottile/pyterminalsize)
[![Coverage Status](https://img.shields.io/coveralls/asottile/pyterminalsize.svg?branch=master)](https://coveralls.io/r/asottile/pyterminalsize)
[![Build status](https://ci.appveyor.com/api/projects/status/lqsw8yuow377kde6/branch/master?svg=true)](https://ci.appveyor.com/project/asottile/pyterminalsize/branch/master)

pyterminalsize
===================

A package to provide access to terminal size.

It uses the following heuristics:
- It first attemps the backported `shutil.get_terminal_size` (from python3.5)
    - Unlike the stdlib implementation it will try each of stdin, stdout, and
      stderr to find terminal size whereas the stdlib only checks stdout.
    - This means that terminal size can still be reported when piping as long
      as one or more of the streams is not piped.
- It then falls back to the `tput` executable (so cygwin works)
- Failing all that, it returns a specified fallback (or `(80, 24)`)

## Usage

```python
>>> from pyterminalsize import get_terminal_size
>>> get_terminal_size()
Size(columns=80, lines=61, source='stdin')
```

`source` can be any of the values specified in `SizeSource`

```python
SizeSource(
    environment='environment',
    stdin='stdin',
    stdout='stdout',
    stderr='stderr',
    tput='tput',
    fallback='fallback',
)
```

## Installation

`pip install pyterminalsize`
