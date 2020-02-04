# __init__.py

import os
import pkg_resources 

try:
    spawn_class_name = os.environ['WEXPECT_SPAWN_CLASS']
except KeyError:
    spawn_class_name = 'legacy_wexpect'

from .legacy_wexpect import ConsoleReader
        

from .console_reader import ConsoleReaderSocket
from .console_reader import ConsoleReaderPipe

from .host import SpawnSocket
from .host import SpawnPipe
from .host import searcher_string
from .host import searcher_re
from .legacy_wexpect import join_args

try:
    spawn = globals()[spawn_class_name]
except KeyError:
    print(f'Error: no spawn class: {spawn_class_name}')
    raise
    
# The version is handled by the package: pbr, which derives the version from the git tags.
try:
    __version__ = pkg_resources.require("wexpect")[0].version
except: # pragma: no cover
    __version__ = '0.0.1.unkowndev0'
    
__all__ = ['ConsoleReaderSocket', 'ConsoleReaderPipe', 'spawn', 'SpawnPipe', 'ConsoleReader', 'join_args']
