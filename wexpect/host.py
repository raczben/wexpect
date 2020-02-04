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


def run (command, timeout=-1, withexitstatus=False, events=None, extra_args=None, logfile=None,
         cwd=None, env=None, **kwargs):
    """
    This function runs the given command; waits for it to finish; then
    returns all output as a string. STDERR is included in output. If the full
    path to the command is not given then the path is searched.

    Note that lines are terminated by CR/LF (\\r\\n) combination even on
    UNIX-like systems because this is the standard for pseudo ttys. If you set
    'withexitstatus' to true, then run will return a tuple of (command_output,
    exitstatus). If 'withexitstatus' is false then this returns just
    command_output.

    The run() function can often be used instead of creating a spawn instance.
    For example, the following code uses spawn::

        child = spawn('scp foo myname@host.example.com:.')
        child.expect ('(?i)password')
        child.sendline (mypassword)

    The previous code can be replace with the following::

    Examples
    ========

    Start the apache daemon on the local machine::

        run ("/usr/local/apache/bin/apachectl start")

    Check in a file using SVN::

        run ("svn ci -m 'automatic commit' my_file.py")

    Run a command and capture exit status::

        (command_output, exitstatus) = run ('ls -l /bin', withexitstatus=1)

    Tricky Examples
    ===============

    The following will run SSH and execute 'ls -l' on the remote machine. The
    password 'secret' will be sent if the '(?i)password' pattern is ever seen::

        run ("ssh username@machine.example.com 'ls -l'", events={'(?i)password':'secret\\n'})

    This will start mencoder to rip a video from DVD. This will also display
    progress ticks every 5 seconds as it runs. For example::

    The 'events' argument should be a dictionary of patterns and responses.
    Whenever one of the patterns is seen in the command out run() will send the
    associated response string. Note that you should put newlines in your
    string if Enter is necessary. The responses may also contain callback
    functions. Any callback is function that takes a dictionary as an argument.
    The dictionary contains all the locals from the run() function, so you can
    access the child spawn object or any other variable defined in run()
    (event_count, child, and extra_args are the most useful). A callback may
    return True to stop the current run process otherwise run() continues until
    the next event. A callback may also return a string which will be sent to
    the child. 'extra_args' is not used by directly run(). It provides a way to
    pass data to a callback function through run() through the locals
    dictionary passed to a callback. """

    from .__init__ import spawn
    if timeout == -1:
        child = spawn(command, maxread=2000, logfile=logfile, cwd=cwd, env=env, **kwargs)
    else:
        child = spawn(command, timeout=timeout, maxread=2000, logfile=logfile, cwd=cwd, env=env, **kwargs)
    if events is not None:
        patterns = list(events.keys())
        responses = list(events.values())
    else:
        patterns=None # We assume that EOF or TIMEOUT will save us.
        responses=None
    child_result_list = []
    event_count = 0
    while 1:
        try:
            index = child.expect (patterns)
            if type(child.after) in (str,):
                child_result_list.append(child.before + child.after)
            else: # child.after may have been a TIMEOUT or EOF, so don't cat those.
                child_result_list.append(child.before)
            if type(responses[index]) in (str,):
                child.send(responses[index])
            elif type(responses[index]) is types.FunctionType:
                callback_result = responses[index](locals())
                sys.stdout.flush()
                if type(callback_result) in (str,):
                    child.send(callback_result)
                elif callback_result:
                    break
            else:
                logger.warning("TypeError ('The callback must be a string or function type.')")
                raise TypeError ('The callback must be a string or function type.')
            event_count = event_count + 1
        except TIMEOUT:
            child_result_list.append(child.before)
            break
        except EOF:
            child_result_list.append(child.before)
            break
    child_result = ''.join(child_result_list)
    if withexitstatus:
        child.wait()
        return (child_result, child.exitstatus)
    else:
        return child_result

      
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
           
    def __str__(self):
        """This returns a human-readable string that represents the state of
        the object. """

        s = []
        s.append(repr(self))
        s.append('command: ' + str(self.command))
        s.append('args: ' + str(self.args))
        s.append('searcher: ' + str(self.searcher))
        s.append('buffer (last 100 chars): ' + str(self.buffer)[-100:])
        s.append('before (last 100 chars): ' + str(self.before)[-100:])
        s.append('after: ' + str(self.after))
        s.append('match: ' + str(self.match))
        s.append('match_index: ' + str(self.match_index))
        s.append('exitstatus: ' + str(self.exitstatus))
        s.append('flag_eof: ' + str(self.flag_eof))
        s.append('host_pid: ' + str(self.host_pid))
        s.append('child_fd: ' + str(self.child_fd))
        s.append('closed: ' + str(self.closed))
        s.append('timeout: ' + str(self.timeout))
        s.append('delimiter: ' + str(self.delimiter))
        s.append('maxread: ' + str(self.maxread))
        s.append('ignorecase: ' + str(self.ignorecase))
        s.append('searchwindowsize: ' + str(self.searchwindowsize))
        s.append('delaybeforesend: ' + str(self.delaybeforesend))
        s.append('delayafterterminate: ' + str(self.delayafterterminate))
        return '\n'.join(s)

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
              
        self.console_class_parameters.update({
                'host_pid': self.host_pid,
                'local_echo': self.echo,
                'interact': self.interact_state,
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
        
    def connect_to_child(self):
        pipe_name = 'wexpect_{}'.format(self.console_pid)
        pipe_full_path = r'\\.\pipe\{}'.format(pipe_name)
        logger.debug(f'Trying to connect to pipe: {pipe_full_path}')
        while True:
            try:
                self.pipe = win32file.CreateFile(
                    pipe_full_path,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None
                )
                logger.debug('Pipe found')
                res = win32pipe.SetNamedPipeHandleState(self.pipe, win32pipe.PIPE_READMODE_MESSAGE, None, None)
                if res == 0:
                    logger.debug(f"SetNamedPipeHandleState return code: {res}")
                return
            except pywintypes.error as e:
                if e.args[0] == winerror.ERROR_FILE_NOT_FOUND:  #2
                    logger.debug("no pipe, trying again in a bit later")
                    time.sleep(0.2)
                else:
                    raise
    
    def disconnect_from_child(self):
        if self.pipe:
            win32file.CloseHandle(self.pipe)
            
    def read_nonblocking (self, size = 1):
        """This reads at most size characters from the child application. If
        the end of file is read then an EOF exception will be raised.

        This is not effected by the 'size' parameter, so if you call
        read_nonblocking(size=100, timeout=30) and only one character is
        available right away then one character will be returned immediately.
        It will not wait for 30 seconds for another 99 characters to come in.

        This is a wrapper around Wtty.read(). """

        if self.closed:
            logger.warning('I/O operation on closed file in read_nonblocking().')
            raise ValueError ('I/O operation on closed file in read_nonblocking().')
            
        try:
            s = win32file.ReadFile(self.pipe, size)[1]
            
            if s:
                logger.debug(f'Readed: {s}')
            else:
                logger.spam(f'Readed: {s}')
                
            if b'\x04' in s:
                self.flag_eof = True
                logger.info("EOF: EOF character has been arrived")
                raise EOF('EOF character has been arrived')
                
            return s.decode()
        except pywintypes.error as e:
            if e.args[0] == winerror.ERROR_BROKEN_PIPE:   #109
                self.flag_eof = True
                logger.info("EOF('broken pipe, bye bye')")
                raise EOF('broken pipe, bye bye')
            elif e.args[0] == winerror.ERROR_NO_DATA:
                '''232 (0xE8): The pipe is being closed.
                '''
                self.flag_eof = True
                logger.info("EOF('The pipe is being closed.')")
                raise EOF('The pipe is being closed.')
            else:
                raise
    
    def _send_impl(self, s):
        """This sends a string to the child process. This returns the number of
        bytes written. If a log file was set then the data is also written to
        the log. """
        if isinstance(s, str):
            s = str.encode(s)
        try:
            if s:
                logger.debug(f"Writing: {s}")
            win32file.WriteFile(self.pipe, s)
            logger.spam(f"WriteFile finished.")
        except pywintypes.error as e:
            if e.args[0] == winerror.ERROR_BROKEN_PIPE:   #109
                logger.info("EOF: broken pipe, bye bye")
                raise EOF("broken pipe, bye bye")
            elif e.args[0] == winerror.ERROR_NO_DATA:
                '''232 (0xE8)
                The pipe is being closed.
                '''
                logger.info("The pipe is being closed.")
                raise EOF("The pipe is being closed.")
            else:
                raise            
        return len(s)
    
    def kill(self, sig=signal.SIGTERM):
        """Sig == sigint for ctrl-c otherwise the child is terminated."""
        try:
            logger.info(f'Sending kill signal: {sig}')
            self.send(SIGNAL_CHARS[sig])
            self.terminated = True
        except EOF as e:
            logger.info(e)


class SpawnSocket(SpawnBase):
    pass

class searcher_re (object):
    pass
    
    
class searcher_string (object):
    pass