"""Wexpect is a Windows variant of pexpect https://pexpect.readthedocs.io.

Wexpect is a Python module for spawning child applications and controlling
them automatically. Wexpect can be used for automating interactive applications
such as ssh, ftp, passwd, telnet, etc. It can be used to a automate setup
scripts for duplicating software package installations on different servers. It
can be used for automated software testing. Wexpect is in the spirit of Don
Libes' Expect, but Wexpect is pure Python. Other Expect-like modules for Python
require TCL and Expect or require C extensions to be compiled. Wexpect does not
use C, Expect, or TCL extensions. 

There are two main interfaces to Wexpect -- the function, run() and the class,
spawn. You can call the run() function to execute a command and return the
output. This is a handy replacement for os.system().

For example::

    wexpect.run('ls -la')

The more powerful interface is the spawn class. You can use this to spawn an
external child command and then interact with the child by sending lines and
expecting responses.

For example::

    child = wexpect.spawn('scp foo myname@host.example.com:.')
    child.expect('Password:')
    child.sendline(mypassword)

This works even for commands that ask for passwords or other input outside of
the normal stdio streams.

Spawn file is the main (aka. host) class of the wexpect. The user call Spawn, which
start the console_reader as a subprocess, which starts the read child.

Credits: Noah Spurrier, Richard Holden, Marco Molteni, Kimberley Burchett,
Robert Stone, Hartmut Goebel, Chad Schroeder, Erick Tryzelaar, Dave Kirby, Ids
vander Molen, George Todd, Noel Taylor, Nicolas D. Cesar, Alexander Gattin,
Geoffrey Marshall, Francisco Lourenco, Glen Mabey, Karthik Gurusamy, Fernando
Perez, Corey Minyard, Jon Cohen, Guillaume Chazarain, Andrew Ryan, Nick
Craig-Wood, Andrew Stone, Jorgen Grahn, Benedek Racz

Free, open source, and all that good stuff.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Wexpect Copyright (c) 2019 Benedek Racz

"""

import time
import sys
import os
import shutil
import re
import traceback
import types
import psutil
import signal
import socket
import logging

import windll
import pywintypes
import win32process
import win32con
import win32file
import winerror
import win32pipe

from .wexpect_util import ExceptionPexpect
from .wexpect_util import EOF
from .wexpect_util import TIMEOUT
from .wexpect_util import split_command_line
from .wexpect_util import init_logger
from .wexpect_util import EOF_CHAR
from .wexpect_util import SIGNAL_CHARS

logger = logging.getLogger('wexpect')
        
init_logger(logger)


      
class SpawnBase:
    def __init__(self, command, args=[], timeout=30, maxread=60000, searchwindowsize=None,
        logfile=None, cwd=None, env=None, codepage=None, echo=True, safe_exit=True, interact=False, **kwargs):
        """This starts the given command in a child process. This does all the
        fork/exec type of stuff for a pty. This is called by __init__. If args
        is empty then command will be parsed (split on spaces) and args will be
        set to parsed arguments. 
        
        The pid and child_fd of this object get set by this method.
        Note that it is difficult for this method to fail.
        You cannot detect if the child process cannot start.
        So the only way you can tell if the child process started
        or not is to try to read from the file descriptor. If you get
        EOF immediately then it means that the child is already dead.
        That may not necessarily be bad because you may haved spawned a child
        that performs some task; creates no stdout output; and then dies.
        """
        self.host_pid = os.getpid() # That's me
        self.console_process = None
        self.console_pid = None
        self.child_process = None
        self.child_pid = None
        
        self.safe_exit = safe_exit
        self.searcher = None
        self.ignorecase = False
        self.before = None
        self.after = None
        self.match = None
        self.match_index = None
        self.terminated = True
        self.exitstatus = None
        self.status = None # status returned by os.waitpid
        self.flag_eof = False
        self.flag_child_finished = False
        self.child_fd = -1 # initially closed
        self.timeout = timeout
        self.delimiter = EOF
        self.cwd = cwd
        self.codepage = codepage
        self.env = env
        self.echo = echo
        self.maxread = maxread # max bytes to read at one time into buffer
        self.delaybeforesend = 0.1 # Sets sleep time used just before sending data to child. Time in seconds.
        self.delayafterterminate = 0.1 # Sets delay in terminate() method to allow kernel time to update process status. Time in seconds.
        self.buffer = '' # This is the read buffer. See maxread.
        self.searchwindowsize = searchwindowsize # Anything before searchwindowsize point is preserved, but not searched.
        self.interact_state = interact
        

        # If command is an int type then it may represent a file descriptor.
        if type(command) == type(0):
            logger.warning("ExceptionPexpect('Command is an int type. If this is a file descriptor then maybe you want to use fdpexpect.fdspawn which takes an existing file descriptor instead of a command string.')")
            raise ExceptionPexpect('Command is an int type. If this is a file descriptor then maybe you want to use fdpexpect.fdspawn which takes an existing file descriptor instead of a command string.')

        if type (args) != type([]):
            logger.warning("TypeError ('The argument, args, must be a list.')")
            raise TypeError ('The argument, args, must be a list.')
   
        if args == []:
            self.args = split_command_line(command)
            self.command = self.args[0]
        else:
            self.args = args[:] # work with a copy
            self.args.insert (0, command)
            self.command = command    
            
        command_with_path = shutil.which(self.command)
        if command_with_path is None:
            logger.warning('The command was not found or was not executable: %s.' % self.command)
            raise ExceptionPexpect ('The command was not found or was not executable: %s.' % self.command)
        self.command = command_with_path
        self.args[0] = self.command

        self.name = '<' + ' '.join (self.args) + '>'      
            
        self.terminated = False
        self.closed = False
        
        self.child_fd = self.startChild(self.args, self.env)
        self.get_child_process()
        logger.info(f'Child pid: {self.child_pid}  Console pid: {self.console_pid}')
#        self.connect_to_child()
        
    def __del__(self):
        """This makes sure that no system resources are left open. Python only
        garbage collects Python objects, not the child console."""
        
        try:
            logger.info('Deleting...')
#            if self.child_process is not None:
#                self.terminate()
#                self.disconnect_from_child()
#                if self.safe_exit:
#                    self.wait()
        except:
            traceback.print_exc()
            logger.warning(traceback.format_exc())
           
    def startChild(self, args, env):
        si = win32process.GetStartupInfo()
        si.dwFlags = win32process.STARTF_USESHOWWINDOW
        si.wShowWindow = win32con.SW_HIDE
    
        dirname = os.path.dirname(sys.executable 
                                  if getattr(sys, 'frozen', False) else 
                                  os.path.abspath(__file__))
        spath = [os.path.dirname(dirname)]
        pyargs = ['-c']
        if getattr(sys, 'frozen', False):
            # If we are running 'frozen', add library.zip and lib\library.zip to sys.path
            # py2exe: Needs appropriate 'zipfile' option in setup script and 'bundle_files' 3
            spath.append(os.path.join(dirname, 'library.zip'))
            spath.append(os.path.join(dirname, 'library.zip', 
                                      os.path.basename(os.path.splitext(sys.executable)[0])))
            if os.path.isdir(os.path.join(dirname, 'lib')):
                dirname = os.path.join(dirname, 'lib')
                spath.append(os.path.join(dirname, 'library.zip'))
                spath.append(os.path.join(dirname, 'library.zip', 
                                          os.path.basename(os.path.splitext(sys.executable)[0])))
            pyargs.insert(0, '-S')  # skip 'import site'
        
        if getattr(sys, 'frozen', False):
            python_executable = os.path.join(dirname, 'python.exe') 
        else:
            python_executable = os.path.join(os.path.dirname(sys.executable), 'python.exe')
              
        cp = self.codepage or windll.kernel32.GetACP()
        
        self.console_class_parameters.update({
                'host_pid': self.host_pid,
                'local_echo': self.echo,
                'interact': self.interact_state,
                'cp': cp,
                'just_init': True
                })
        console_class_parameters_kv_pairs = [f'{k}={v}' for k,v in self.console_class_parameters.items() ]
        console_class_parameters_str = ', '.join(console_class_parameters_kv_pairs)
        
        child_class_initializator = f"cons = wexpect.{self.console_class_name}(wexpect.join_args({args}), {console_class_parameters_str});"
        
        commandLine = '"%s" %s "%s"' % (python_executable, 
                                        ' '.join(pyargs), 
                                        "import sys;"
                                        f"sys.path = {spath} + sys.path;"
                                        "import wexpect;"
                                        "import time;"
                                        "wexpect.console_reader.logger.info('loggerStart.');"
                                        f"{child_class_initializator}"
                                        "wexpect.console_reader.logger.info(f'Console finished2. {cons.child_exitstatus}');"
                                        "sys.exit(cons.child_exitstatus)"
                                        )
        
        logger.info(f'Console starter command:{commandLine}')
        
        _, _, self.console_pid, __otid = win32process.CreateProcess(None, commandLine, None, None, False, 
                                                        win32process.CREATE_NEW_CONSOLE, None, self.cwd, si)
        
    def get_console_process(self, force=False):
        if force or self.console_process is None:
            self.console_process = psutil.Process(self.console_pid)
        return self.console_process
    
    def get_child_process(self, force=False):
        if force or self.console_process is None:
            self.child_process = self.get_console_process()
            self.child_pid = self.child_process.pid
            return self.child_process
       
class SpawnPipe(SpawnBase):
    
    def __init__(self, command, args=[], timeout=30, maxread=60000, searchwindowsize=None,
        logfile=None, cwd=None, env=None, codepage=None, echo=True, interact=False, **kwargs):
        self.pipe = None
        self.console_class_name = 'ConsoleReaderPipe'
        self.console_class_parameters = {}
        
        super().__init__(command=command, args=args, timeout=timeout, maxread=maxread,
             searchwindowsize=searchwindowsize, cwd=cwd, env=env, codepage=codepage, echo=echo, interact=interact)
    
        self.delayafterterminate = 1 # Sets delay in terminate() method to allow kernel time to update process status. Time in seconds.
        

class SpawnSocket(SpawnBase):
    pass

class searcher_re (object):
    pass
    
    
class searcher_string (object):
    pass