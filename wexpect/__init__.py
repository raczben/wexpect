# __init__.py

import os

from .wexpect_util import split_command_line
from .wexpect_util import join_args
from .wexpect_util import ExceptionPexpect
from .wexpect_util import EOF
from .wexpect_util import TIMEOUT

from .console_reader import ConsoleReaderSocket
from .console_reader import ConsoleReaderPipe

from .host import SpawnSocket
from .host import SpawnPipe
from .host import run

try:
    spawn_class_name = os.environ['WEXPECT_SPAWN_CLASS']
    try:
        spawn = globals()[spawn_class_name]
    except KeyError:
        print(f'Error: no spawn class: {spawn_class_name}')
        print('Using SpawnSocket.')
        spawn = SpawnSocket
except KeyError:
    spawn = SpawnSocket

__all__ = ['split_command_line', 'join_args', 'ExceptionPexpect', 'EOF', 'TIMEOUT',
           'ConsoleReaderSocket', 'ConsoleReaderPipe', 'spawn', 'SpawnSocket', 'SpawnPipe', 'run']
