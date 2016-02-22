[![Build Status](https://travis-ci.org/asottile/pyterminalsize.svg?branch=master)](https://travis-ci.org/asottile/pyterminalsize)
[![Coverage Status](https://img.shields.io/coveralls/asottile/pyterminalsize.svg?branch=master)](https://coveralls.io/r/asottile/pyterminalsize)
[![Build status](https://ci.appveyor.com/api/projects/status/lqsw8yuow377kde6/branch/master?svg=true)](https://ci.appveyor.com/project/asottile/pyterminalsize/branch/master)

pyterminalsize
===================

A package to provide access to terminal size.

It uses the following heuristics:
- First it attemps the backported `shutil.get_terminal_size` (from python3.5)
- Then it falls back to `tput` executable (so cygwin works)
- Failing all that, it returns a specified fallback (or `(80, 24)`)

The structure it returns looks like:

```python
Size(columns=80, lines=24, source='fallback')
```

Where source can be any of the values specified in `SizeSource`

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
