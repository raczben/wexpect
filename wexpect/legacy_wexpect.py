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

#
# wexpect is windows only. Use pexpect on linux like systems.
#
import sys
if sys.platform != 'win32': # pragma: no cover
    raise ImportError ("""sys.platform != 'win32': Wexpect supports only Windows.
Pexpect is intended for UNIX-like operating systems.""")

#
# Import built in modules
#
import logging
import os
import time
import re
import shutil
import types
import traceback
import signal
import pkg_resources 
from io import StringIO

try:
    from ctypes import windll
    import pywintypes
    import win32console
    import win32process
    import win32con
    import win32gui
    import win32api
    import win32file
    import winerror
except ImportError as e: # pragma: no cover
    raise ImportError(str(e) + "\nThis package requires the win32 python packages.\r\nInstall with pip install pywin32")

# 
# System-wide constants
#    
screenbufferfillchar = '\4'
maxconsoleY = 8000

# The version is handled by the package: pbr, which derives the version from the git tags.
try:
    __version__ = pkg_resources.require("wexpect")[0].version
except: # pragma: no cover
    __version__ = '0.0.1.unkowndev0'

__all__ = ['ExceptionPexpect', 'EOF', 'TIMEOUT', 'spawn', 'run', 'which',
    'split_command_line', '__version__']

#
# Create logger: We write logs only to file. Printing out logs are dangerous, because of the deep
# console manipulation.
#
pid=os.getpid()
logger = logging.getLogger('wexpect_legacy')
try:
    logger_level = os.environ['WEXPECT_LOGGER_LEVEL']
    logger.setLevel(logger_level)
    fh = logging.FileHandler(f'wexpect_legacy_{pid}.log', 'w', 'utf-8')
    formatter = logging.Formatter('%(asctime)s - %(filename)s::%(funcName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
except KeyError:
    logger.setLevel(logging.ERROR)

# Test the logger
logger.info('wexpect imported; logger working')

####################################################################################################
#
#        Exceptions
#
####################################################################################################

class ExceptionPexpect(Exception):
    """Base class for all exceptions raised by this module.
    """

    def __init__(self, value):

        self.value = value

    def __str__(self):

        return str(self.value)

    def get_trace(self):
        """This returns an abbreviated stack trace with lines that only concern
        the caller. In other words, the stack trace inside the Wexpect module
        is not included. """

        tblist = traceback.extract_tb(sys.exc_info()[2])
        tblist = [item for item in tblist if self.__filter_not_wexpect(item)]
        tblist = traceback.format_list(tblist)
        return ''.join(tblist)

    def __filter_not_wexpect(self, trace_list_item):
        """This returns True if list item 0 the string 'wexpect.py' in it. """

        if trace_list_item[0].find('wexpect.py') == -1:
            return True
        else:
            return False


class EOF(ExceptionPexpect):
    """Raised when EOF is read from a child. This usually means the child has exited.
    The user can wait to EOF, which means he waits the end of the execution of the child process."""

class TIMEOUT(ExceptionPexpect):
    """Raised when a read time exceeds the timeout. """


def run (command, timeout=-1, withexitstatus=False, events=None, extra_args=None, logfile=None,
    cwd=None, env=None, echo=True):

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

    if timeout == -1:
        child = spawn(command, maxread=2000, logfile=logfile, cwd=cwd, env=env)
    else:
        child = spawn(command, timeout=timeout, maxread=2000, logfile=logfile, cwd=cwd, env=env)
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
                logger.info('TypeError: The callback must be a string or function type.')
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
        child.close()
        return (child_result, child.exitstatus)
    else:
        return child_result

def spawn(command, args=[], timeout=30, maxread=2000, searchwindowsize=None, logfile=None, cwd=None,
    env=None, codepage=None, echo=True, **kwargs):
    """This is the most essential function. The command parameter may be a string that
    includes a command and any arguments to the command. For example::

        child = wexpect.spawn ('/usr/bin/ftp')
        child = wexpect.spawn ('/usr/bin/ssh user@example.com')
        child = wexpect.spawn ('ls -latr /tmp')

    You may also construct it with a list of arguments like so::

        child = wexpect.spawn ('/usr/bin/ftp', [])
        child = wexpect.spawn ('/usr/bin/ssh', ['user@example.com'])
        child = wexpect.spawn ('ls', ['-latr', '/tmp'])

    After this the child application will be created and will be ready to
    talk to. For normal use, see expect() and send() and sendline().

    Remember that Wexpect does NOT interpret shell meta characters such as
    redirect, pipe, or wild cards (>, |, or *). This is a common mistake.
    If you want to run a command and pipe it through another command then
    you must also start a shell. For example::

        child = wexpect.spawn('/bin/bash -c "ls -l | grep LOG > log_list.txt"')
        child.expect(wexpect.EOF)

    The second form of spawn (where you pass a list of arguments) is useful
    in situations where you wish to spawn a command and pass it its own
    argument list. This can make syntax more clear. For example, the
    following is equivalent to the previous example::

        shell_cmd = 'ls -l | grep LOG > log_list.txt'
        child = wexpect.spawn('/bin/bash', ['-c', shell_cmd])
        child.expect(wexpect.EOF)

    The maxread attribute sets the read buffer size. This is maximum number
    of bytes that Wexpect will try to read from a TTY at one time. Setting
    the maxread size to 1 will turn off buffering. Setting the maxread
    value higher may help performance in cases where large amounts of
    output are read back from the child. This feature is useful in
    conjunction with searchwindowsize.

    The searchwindowsize attribute sets the how far back in the incomming
    seach buffer Wexpect will search for pattern matches. Every time
    Wexpect reads some data from the child it will append the data to the
    incomming buffer. The default is to search from the beginning of the
    imcomming buffer each time new data is read from the child. But this is
    very inefficient if you are running a command that generates a large
    amount of data where you want to match The searchwindowsize does not
    effect the size of the incomming data buffer. You will still have
    access to the full buffer after expect() returns.

    The delaybeforesend helps overcome a weird behavior that many users
    were experiencing. The typical problem was that a user would expect() a
    "Password:" prompt and then immediately call sendline() to send the
    password. The user would then see that their password was echoed back
    to them. Passwords don't normally echo. The problem is caused by the
    fact that most applications print out the "Password" prompt and then
    turn off stdin echo, but if you send your password before the
    application turned off echo, then you get your password echoed.
    Normally this wouldn't be a problem when interacting with a human at a
    real keyboard. If you introduce a slight delay just before writing then
    this seems to clear up the problem. This was such a common problem for
    many users that I decided that the default wexpect behavior should be
    to sleep just before writing to the child application. 1/20th of a
    second (50 ms) seems to be enough to clear up the problem. You can set
    delaybeforesend to 0 to return to the old behavior. Most Linux machines
    don't like this to be below 0.03. I don't know why.

    Note that spawn is clever about finding commands on your path.
    It uses the same logic that "which" uses to find executables.

    If you wish to get the exit status of the child you must call the
    close() method. The exit status of the child will be stored in self.exitstatus.
    If the child exited normally then exitstatus will store the exit return code.
    """

    logger.debug('=' * 80)
    logger.debug('Buffer size: %s' % maxread)
    if searchwindowsize:
        logger.debug('Search window size: %s' % searchwindowsize)
    logger.debug('Timeout: %ss' % timeout)
    if env:
        logger.debug('Environment:')
        for name in env:
            logger.debug('\t%s=%s' % (name, env[name]))
    if cwd:
        logger.debug('Working directory: %s' % cwd)
        
    return spawn_windows(command, args, timeout, maxread, searchwindowsize, logfile, cwd, env,
                             codepage, echo=echo)        

class spawn_windows ():
    """This is the main class interface for Wexpect. Use this class to start
    and control child applications. """

    def __init__(self, command, args=[], timeout=30, maxread=60000, searchwindowsize=None,
        logfile=None, cwd=None, env=None, codepage=None, echo=True):
        """ The spawn_windows constructor. Do not call it directly. Use spawn(), or run() instead.
        """
        self.codepage = codepage
        
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr

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
        self.pid = None
        self.child_fd = -1 # initially closed
        self.timeout = timeout
        self.delimiter = EOF
        self.logfile = logfile
        self.logfile_read = None # input from child (read_nonblocking)
        self.logfile_send = None # output to send (send, sendline)
        self.maxread = maxread # max bytes to read at one time into buffer
        self.buffer = '' # This is the read buffer. See maxread.
        self.searchwindowsize = searchwindowsize # Anything before searchwindowsize point is preserved, but not searched.
        self.delaybeforesend = 0.05 # Sets sleep time used just before sending data to child. Time in seconds.
        self.delayafterterminate = 0.1 # Sets delay in terminate() method to allow kernel time to update process status. Time in seconds.
        self.name = '<' + repr(self) + '>' # File-like object.
        self.closed = True # File-like object.
        self.ocwd = os.getcwd()
        self.cwd = cwd
        self.env = env
        
        # allow dummy instances for subclasses that may not use command or args.
        if command is None:
            self.command = None
            self.args = None
            self.name = '<wexpect factory incomplete>'
        else:
            self._spawn(command, args, echo=echo)

    def __del__(self):
        """This makes sure that no system resources are left open. Python only
        garbage collects Python objects, not the child console."""
        
        try:
            self.wtty.terminate_child()
        except:
            pass
           
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
        s.append('pid: ' + str(self.pid))
        s.append('child_fd: ' + str(self.child_fd))
        s.append('closed: ' + str(self.closed))
        s.append('timeout: ' + str(self.timeout))
        s.append('delimiter: ' + str(self.delimiter))
        s.append('logfile: ' + str(self.logfile))
        s.append('logfile_read: ' + str(self.logfile_read))
        s.append('logfile_send: ' + str(self.logfile_send))
        s.append('maxread: ' + str(self.maxread))
        s.append('ignorecase: ' + str(self.ignorecase))
        s.append('searchwindowsize: ' + str(self.searchwindowsize))
        s.append('delaybeforesend: ' + str(self.delaybeforesend))
        s.append('delayafterterminate: ' + str(self.delayafterterminate))
        return '\n'.join(s)
 
    def _spawn(self,command,args=[], echo=True):
        """This starts the given command in a child process. This does all the
        fork/exec type of stuff for a pty. This is called by __init__. If args
        is empty then command will be parsed (split on spaces) and args will be
        set to parsed arguments. """

        # The pid and child_fd of this object get set by this method.
        # Note that it is difficult for this method to fail.
        # You cannot detect if the child process cannot start.
        # So the only way you can tell if the child process started
        # or not is to try to read from the file descriptor. If you get
        # EOF immediately then it means that the child is already dead.
        # That may not necessarily be bad because you may haved spawned a child
        # that performs some task; creates no stdout output; and then dies.

        # If command is an int type then it may represent a file descriptor.
        if type(command) == type(0):
            logger.info('ExceptionPexpect: Command is an int type. If this is a file descriptor then maybe you want to use fdpexpect.fdspawn which takes an existing file descriptor instead of a command string.')
            raise ExceptionPexpect ('Command is an int type. If this is a file descriptor then maybe you want to use fdpexpect.fdspawn which takes an existing file descriptor instead of a command string.')

        if type (args) != type([]):
            logger.info('TypeError: The argument, args, must be a list.')
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
           logger.info('ExceptionPexpect: The command was not found or was not executable: %s.' % self.command)
           raise ExceptionPexpect ('The command was not found or was not executable: %s.' % self.command)
        self.command = command_with_path
        self.args[0] = self.command

        self.name = '<' + ' '.join (self.args) + '>'

        #assert self.pid is None, 'The pid member should be None.'
        #assert self.command is not None, 'The command member should not be None.'

        self.wtty = Wtty(codepage=self.codepage, echo=echo)        
    
        if self.cwd is not None:
            os.chdir(self.cwd)
        
        self.child_fd = self.wtty.spawn(self.command, self.args, self.env)
        
        if self.cwd is not None:
            # Restore the original working dir
            os.chdir(self.ocwd)
            
        self.terminated = False
        self.closed = False
        self.pid = self.wtty.pid
        

##############################################################################
# End of spawn_windows class
##############################################################################

class Wtty:

    def __init__(self, timeout=30, codepage=None, echo=True):
        self.__buffer = StringIO()
        self.__bufferY = 0
        self.__currentReadCo = win32console.PyCOORDType(0, 0)
        self.__consSize = [80, 16000]
        self.__parentPid = 0
        self.__oproc = 0
        self.conpid = 0
        self.__otid = 0
        self.__switch = True
        self.__childProcess = None
        self.__conProcess = None
        self.codepage = codepage
        self.console = False
        self.lastRead = 0
        self.lastReadData = ""
        self.pid = None
        self.processList = []
        self.__consout = None
        # We need a timeout for connecting to the child process
        self.timeout = timeout
        self.totalRead = 0
        self.local_echo = echo
            
    def spawn(self, command, args=[], env=None):
        """Spawns spawner.py with correct arguments."""
        
        ts = time.time()
        self.startChild(args, env)
            
        logger.info(f"Fetch child's process and pid...")
        
        self.__conProcess = win32api.OpenProcess(
            win32con.PROCESS_TERMINATE | win32con.PROCESS_QUERY_INFORMATION, False, self.conpid)
            
        logger.info(f"Child's pid: {self.pid}")
        
        winHandle = int(win32console.GetConsoleWindow())
        
        self.__switch = True
        
        if winHandle != 0:
            self.__parentPid = win32process.GetWindowThreadProcessId(winHandle)[1]    
            # Do we have a console attached? Do not rely on winHandle, because
            # it will also be non-zero if we didn't have a console, and then 
            # spawned a child process! Using sys.stdout.isatty() seems safe
            self.console = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
            # If the original process had a console, record a list of attached
            # processes so we can check if we need to reattach/reallocate the 
            # console later
            self.processList = win32console.GetConsoleProcessList()
        else:
            self.switchTo(False)
            self.__switch = False
   
    def startChild(self, args, env):
        si = win32process.GetStartupInfo()
        si.dwFlags = win32process.STARTF_USESHOWWINDOW
        si.wShowWindow = win32con.SW_HIDE
        # Determine the directory of wexpect.py or, if we are running 'frozen'
        # (eg. py2exe deployment), of the packed executable

        dirname = os.path.dirname(sys.executable 
                                  if getattr(sys, 'frozen', False) else 
                                  os.path.abspath(__file__))
        if getattr(sys, 'frozen', False):
            logdir = os.path.splitext(sys.executable)[0]
        else:
            logdir = dirname
        logdir = os.path.basename(logdir)
        spath = [os.path.dirname(dirname)]
        pyargs = ['-c']
        if getattr(sys, 'frozen', False):
            # If we are running 'frozen', add library.zip and lib\library.zip
            # to sys.path
            # py2exe: Needs appropriate 'zipfile' option in setup script and 
            # 'bundle_files' 3
            spath.append(os.path.join(dirname, 'library.zip'))
            spath.append(os.path.join(dirname, 'library.zip', 
                                      os.path.basename(os.path.splitext(sys.executable)[0])))
            if os.path.isdir(os.path.join(dirname, 'lib')):
                dirname = os.path.join(dirname, 'lib')
                spath.append(os.path.join(dirname, 'library.zip'))
                spath.append(os.path.join(dirname, 'library.zip', 
                                          os.path.basename(os.path.splitext(sys.executable)[0])))
            pyargs.insert(0, '-S')  # skip 'import site'
        pid = win32process.GetCurrentProcessId()
        tid = win32api.GetCurrentThreadId()
        cp = self.codepage or windll.kernel32.GetACP()
        # If we are running 'frozen', expect python.exe in the same directory
        # as the packed executable.
        # py2exe: The python executable can be included via setup script by 
        # adding it to 'data_files'
        
        if getattr(sys, 'frozen', False):
            python_executable = os.path.join(dirname, 'python.exe') 
        else:
            python_executable = os.path.join(os.path.dirname(sys.executable), 'python.exe')
            
        commandLine = '"%s" %s "%s"' % (python_executable, 
                                        ' '.join(pyargs), 
                                        f"import sys; sys.path = {spath} + sys.path;"
                                        f"args = {args}; import wexpect;"
                                        f"wexpect.ConsoleReaderPipe(wexpect.join_args(args), {pid}, just_init=True)"
                                        )
                                        
        logger.info(f'CreateProcess: {commandLine}')
        
        self.__oproc, x, self.conpid, self.__otid = win32process.CreateProcess(None, commandLine, None, None, False, 
                                                                  win32process.CREATE_NEW_CONSOLE, env, None, si)
        logger.info(f'self.__oproc: {self.__oproc}')
        logger.info(f'x: {x}')
        logger.info(f'self.conpid: {self.conpid}')
        logger.info(f'self.__otid: {self.__otid}')
   
    def terminate_child(self):
        """Terminate the child process."""
        win32api.TerminateProcess(self.__childProcess, 1)
        # win32api.win32process.TerminateProcess(self.__childProcess, 1)
        
class ConsoleReader: 
    pass
   
class searcher_string (object):
    pass

class searcher_re (object):
    pass

def join_args(args):
    """Joins arguments into a command line. It quotes all arguments that contain
    spaces or any of the characters ^!$%&()[]{}=;'+,`~"""
    commandline = []
    for arg in args:
        if re.search('[\^!$%&()[\]{}=;\'+,`~\s]', arg):
            arg = '"%s"' % arg
        commandline.append(arg)
    return ' '.join(commandline)

def split_command_line(command_line, escape_char = '^'):
    """This splits a command line into a list of arguments. It splits arguments
    on spaces, but handles embedded quotes, doublequotes, and escaped
    characters. It's impossible to do this with a regular expression, so I
    wrote a little state machine to parse the command line. """

    arg_list = []
    arg = ''

    # Constants to name the states we can be in.
    state_basic = 0
    state_esc = 1
    state_singlequote = 2
    state_doublequote = 3
    state_whitespace = 4 # The state of consuming whitespace between commands.
    state = state_basic

    for c in command_line:
        if state == state_basic or state == state_whitespace:
            if c == escape_char: # Escape the next character
                state = state_esc
            elif c == r"'": # Handle single quote
                state = state_singlequote
            elif c == r'"': # Handle double quote
                state = state_doublequote
            elif c.isspace():
                # Add arg to arg_list if we aren't in the middle of whitespace.
                if state == state_whitespace:
                    None # Do nothing.
                else:
                    arg_list.append(arg)
                    arg = ''
                    state = state_whitespace
            else:
                arg = arg + c
                state = state_basic
        elif state == state_esc:
            arg = arg + c
            state = state_basic
        elif state == state_singlequote:
            if c == r"'":
                state = state_basic
            else:
                arg = arg + c
        elif state == state_doublequote:
            if c == r'"':
                state = state_basic
            else:
                arg = arg + c

    if arg != '':
        arg_list.append(arg)
    return arg_list
