import sys


__all__ = ('string_types', 'IS_PYTHON2', 'IS_PYTHON3')

IS_PYTHON2 = sys.version_info < (3,)
IS_PYTHON3 = not IS_PYTHON2

string_types = ()


if IS_PYTHON2:
    string_types = (str, globals()['__builtins__']['unicode'])
else:
    string_types = (str,)
