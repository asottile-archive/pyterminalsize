import pyterminalsize


try:
    print(pyterminalsize._from_tput())
except OSError as e:
    print('Caught OSError')
    print(e)
