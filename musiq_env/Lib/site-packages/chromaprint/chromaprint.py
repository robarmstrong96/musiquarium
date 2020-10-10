_bg = {'black': '\033[40m',
       'white': '\033[47m',
       'magenta': '\033[45m',
       'red': '\033[41m',
       'yellow': '\033[43m',
       'green': '\033[42m',
       'cyan': '\033[46m',
       'blue': '\033[44m',
       'default': '\033[49m',
       'user_default': '\033[49m'
       }

_fg = {'black': '\033[30m',
       'white': '\033[37m',
       'magenta': '\033[35m',
       'red': '\033[31m',
       'yellow': '\033[33m',
       'green': '\033[32m',
       'cyan': '\033[36m',
       'blue': '\033[34m',
       'default': '\033[39m',
       'user_default': '\033[39m'
       }

_print = print  # noqa
colors = tuple(i for i in _bg.keys() if i != 'user_default')


def print(*args, bg='user_default', fg='user_default'):
    ''' Replacement print method to print in colors
    *args (str): strings to be printed. Passed as if passing to built-in print method
    bg (str): back

    '''
    _print(_bg[bg], _fg[fg], ' '.join(args), _bg['user_default'], _fg['user_default'], sep='')


def set_default(**kwargs):
    ''' Sets 'user_default' colors
    **kwargs {fg: 'color', bg: 'color'}
    '''
    _bg['user_default'] = _bg[kwargs.get('bg', 'user_default')]
    _fg['user_default'] = _fg[kwargs.get('fg', 'user_default')]
