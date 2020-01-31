import sys

import _pyterminalsize

import pyterminalsize


for fd in (0, 1, 2):
    try:
        # Allow this to fail, we're setting it on all the inputs / outputs
        _pyterminalsize.set_terminal_size(fd, 30, 40)
    except OSError:
        pass

getattr(sys, sys.argv[1]).write(str(pyterminalsize.get_terminal_size()))
