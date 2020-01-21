"""Wexpect is a Windows variant of pexpect https://pexpect.readthedocs.io.

Wexpect is a Python module for spawning child applications and controlling
them automatically. 

console_reader Implements a virtual terminal, and starts the child program.
The main wexpect.Spawn class connect to this class to reach the child's terminal.

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
import logging
import os
import traceback
import pkg_resources 
from io import StringIO

import ctypes
import pywintypes
import win32console
import win32process
import win32con
import win32file
import winerror
import win32pipe
import socket

# 
# System-wide constants
#    
screenbufferfillchar = '\4'
maxconsoleY = 8000
default_port = 4321

# The version is handled by the package: pbr, which derives the version from the git tags.
try:
    __version__ = pkg_resources.require("wexpect")[0].version
except: # pragma: no cover
    __version__ = '0.0.1.unkowndev0'

#
# Create logger: We write logs only to file. Printing out logs are dangerous, because of the deep
# console manipulation.
#
logger = logging.getLogger('wexpect')

def init_logger():
    logger = logging.getLogger('wexpect')
    os.environ['WEXPECT_LOGGER_LEVEL'] = 'DEBUG'
    try:
        logger_level = os.environ['WEXPECT_LOGGER_LEVEL']
        try:
            logger_filename = os.environ['WEXPECT_LOGGER_FILENAME']
        except KeyError:
            pid = os.getpid()
            logger_filename = f'wexpect_{pid}'
        logger.setLevel(logger_level)
        fh = logging.FileHandler(f'{logger_filename}.log', 'w', 'utf-8')
        formatter = logging.Formatter('%(asctime)s - %(filename)s::%(funcName)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except KeyError:
        logger.setLevel(logging.ERROR)

class ConsoleReaderBase:
    """Consol class (aka. client-side python class) for the child.
    
    This class initialize the console starts the child in it and reads the console periodically.
    """

    def __init__(self, path, parent_pid, cp=None, window_size_x=80, window_size_y=25,
                 buffer_size_x=80, buffer_size_y=16000, **kwargs):
        """Initialize the console starts the child in it and reads the console periodically.        

        Args:
            path (str): Child's executable with arguments.
            parent_pid (int): Parent (aka. host) process process-ID
            cp (:obj:, optional): Output console code page.
        """
        self.lastRead  = 0
        self.__bufferY = 0
        self.lastReadData = ""
        self.totalRead = 0
        self.__buffer = StringIO()
        self.__currentReadCo = win32console.PyCOORDType(0, 0)
        self.pipe = None
        self.connection = None
        self.consin = None
        self.consout = None
        self.local_echo = True
        self.pid = os.getpid() 
        
        init_logger()
        logger.info("ConsoleReader started")
        
        if cp:
            try:
                logger.info("Setting console output code page to %s" % cp)
                win32console.SetConsoleOutputCP(cp)
                logger.info("Console output code page: %s" % ctypes.windll.kernel32.GetConsoleOutputCP())
            except Exception as e:
                logger.info(e)
                
        try:
            self.create_connection(**kwargs)
            logger.info('Spawning %s' % path)
            try:
                self.initConsole()
                si = win32process.GetStartupInfo()
                self.__childProcess, _, childPid, self.__tid = win32process.CreateProcess(None, path, None, None, False, 
                                                                             0, None, None, si)
                
            except Exception as e:
                logger.info(e)
                return
            
            time.sleep(.2)
            self.write('ls')
            self.write(os.linesep)
                  
            paused = False
   
            while True:
                consinfo = self.consout.GetConsoleScreenBufferInfo()
                cursorPos = consinfo['CursorPosition']
                self.send_to_host(self.readConsoleToCursor())
                s = self.get_from_host()
                self.write(s)
                
                if win32process.GetExitCodeProcess(self.__childProcess) != win32con.STILL_ACTIVE:
                    time.sleep(.1)
                    try:
                        win32process.TerminateProcess(self.__childProcess, 0)
                    except pywintypes.error as e:
                        """ 'Access denied' happens always? Perhaps if not running as admin (or UAC
                        enabled under Vista/7). Don't log. Child process will exit regardless when 
                        calling sys.exit
                        """
                        if e.args[0] != winerror.ERROR_ACCESS_DENIED:
                            logger.info(e)
                    return
                
                if cursorPos.Y > maxconsoleY and not paused:
                    logger.info('cursorPos %s' % cursorPos)
                    self.suspendThread()
                    paused = True
                    
                if cursorPos.Y <= maxconsoleY and paused:
                    logger.info('cursorPos %s' % cursorPos)
                    self.resumeThread()
                    paused = False
                                    
                time.sleep(.1)
        except:
            logger.error(traceback.format_exc())
            time.sleep(.1)
        finally:
            time.sleep(.1) 
            self.send_to_host(self.readConsoleToCursor())
            time.sleep(1) 
            self.close_connection()
            
    def write(self, s):
        """Writes input into the child consoles input buffer."""
    
        if len(s) == 0:
            return 0
        if s[-1] == '\n':
            s = s[:-1]
        records = [self.createKeyEvent(c) for c in str(s)]
        if not self.consout:
            return ""
            
        # Store the current cursor position to hide characters in local echo disabled mode (workaround).
        consinfo = self.consout.GetConsoleScreenBufferInfo()
        startCo = consinfo['CursorPosition']
        
        # Send the string to console input
        wrote = self.consin.WriteConsoleInput(records)
        
        # Wait until all input has been recorded by the console.
        ts = time.time()
        while self.consin.PeekConsoleInput(8) != ():
            if time.time() > ts + len(s) * .1 + .5:
                break
            time.sleep(.05)
            
        # Hide characters in local echo disabled mode (workaround).
        if not self.local_echo:
            self.consout.FillConsoleOutputCharacter(screenbufferfillchar, len(s), startCo)
            
        return wrote
    
    def createKeyEvent(self, char):
        """Creates a single key record corrosponding to
            the ascii character char."""
        
        evt = win32console.PyINPUT_RECORDType(win32console.KEY_EVENT)
        evt.KeyDown = True
        evt.Char = char
        evt.RepeatCount = 1
        return evt   
            
    def initConsole(self, consout=None, window_size_x=80, window_size_y=25, buffer_size_x=80,
                    buffer_size_y=16000):
        if not consout:
            consout=self.getConsoleOut()
            
        self.consin = win32console.GetStdHandle(win32console.STD_INPUT_HANDLE)
            
        rect = win32console.PySMALL_RECTType(0, 0, window_size_x-1, window_size_y-1)
        consout.SetConsoleWindowInfo(True, rect)
        size = win32console.PyCOORDType(buffer_size_x, buffer_size_y)
        consout.SetConsoleScreenBufferSize(size)
        pos = win32console.PyCOORDType(0, 0)
        # Use NUL as fill char because it displays as whitespace
        # (if we interact() with the child)
        consout.FillConsoleOutputCharacter(screenbufferfillchar, size.X * size.Y, pos) 
        
        consinfo = consout.GetConsoleScreenBufferInfo()
        self.__consSize = consinfo['Size']
        logger.info('self.__consSize: ' + str(self.__consSize))
        self.startCursorPos = consinfo['CursorPosition']  
    
        
    def parseData(self, s):
        """Ensures that special characters are interpretted as
        newlines or blanks, depending on if there written over
        characters or screen-buffer-fill characters."""
    
        strlist = []
        for i, c in enumerate(s):
            if c == screenbufferfillchar:
                if (self.totalRead - self.lastRead + i + 1) % self.__consSize.X == 0:
                    strlist.append('\r\n')
            else:
                strlist.append(c)

        s = ''.join(strlist)
        return s
    
    def getConsoleOut(self):
        consfile = win32file.CreateFile('CONOUT$', 
                                       win32con.GENERIC_READ | win32con.GENERIC_WRITE, 
                                       win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE, 
                                       None, 
                                       win32con.OPEN_EXISTING, 
                                       0, 
                                       0)
                                       
        self.consout = win32console.PyConsoleScreenBufferType(consfile)
        return self.consout
           
    def getCoord(self, offset):
        """Converts an offset to a point represented as a tuple."""
        
        x = offset %  self.__consSize.X
        y = offset // self.__consSize.X
        return win32console.PyCOORDType(x, y)

    def getOffset(self, coord):
        """Converts a tuple-point to an offset."""
        
        return coord.X + coord.Y * self.__consSize.X
        
    def readConsole(self, startCo, endCo):
        """Reads the console area from startCo to endCo and returns it
        as a string."""
        
        if startCo is None:
            startCo = self.startCursorPos 
            startCo.Y = startCo.Y
            
        if endCo is None:
            consinfo = self.consout.GetConsoleScreenBufferInfo()
            endCo = consinfo['CursorPosition']
            endCo= self.getCoord(0 + self.getOffset(endCo))
        
        buff = []
        self.lastRead = 0

        while True:
            startOff = self.getOffset(startCo)
            endOff = self.getOffset(endCo)
            readlen = endOff - startOff
            
            if readlen <= 0:
                break
            
            if readlen > 4000:
                readlen = 4000
            endPoint = self.getCoord(startOff + readlen)

            s = self.consout.ReadConsoleOutputCharacter(readlen, startCo)
            self.lastRead += len(s)
            self.totalRead += len(s)
            buff.append(s)

            startCo = endPoint

        return ''.join(buff)
    
    
    def readConsoleToCursor(self):
        """Reads from the current read position to the current cursor
        position and inserts the string into self.__buffer."""
        
        if not self.consout:
            return ""
    
        consinfo = self.consout.GetConsoleScreenBufferInfo()
        cursorPos = consinfo['CursorPosition']
        
        logger.debug('cursor: %r, current: %r' % (cursorPos, self.__currentReadCo))

        isSameX = cursorPos.X == self.__currentReadCo.X
        isSameY = cursorPos.Y == self.__currentReadCo.Y
        isSamePos = isSameX and isSameY
        
        logger.debug('isSameY: %r' % isSameY)
        logger.debug('isSamePos: %r' % isSamePos)
        
        if isSameY or not self.lastReadData.endswith('\r\n'):
            # Read the current slice again
            self.totalRead -= self.lastRead
            self.__currentReadCo.X = 0
            self.__currentReadCo.Y = self.__bufferY
        
        logger.debug('cursor: %r, current: %r' % (cursorPos, self.__currentReadCo))
        
        raw = self.readConsole(self.__currentReadCo, cursorPos)
        rawlist = []
        while raw:
            rawlist.append(raw[:self.__consSize.X])
            raw = raw[self.__consSize.X:]
        raw = ''.join(rawlist)
        s = self.parseData(raw)
        for i, line in enumerate(reversed(rawlist)):
            if line.endswith(screenbufferfillchar):
                # Record the Y offset where the most recent line break was detected
                self.__bufferY += len(rawlist) - i
                break
        
        logger.debug('lastReadData: %r' % self.lastReadData)
        logger.debug('s: %r' % s)
        
        if isSamePos and self.lastReadData == s:
            logger.debug('isSamePos and self.lastReadData == s')
            s = ''
        
        if s:
            lastReadData = self.lastReadData
            pos = self.getOffset(self.__currentReadCo)
            self.lastReadData = s
            if isSameY or not lastReadData.endswith('\r\n'):
                # Detect changed lines
                self.__buffer.seek(pos)
                buf = self.__buffer.read()
                if raw.startswith(buf):
                    # Line has grown
                    rawslice = raw[len(buf):]
                    # Update last read bytes so line breaks can be detected in parseData
                    lastRead = self.lastRead
                    self.lastRead = len(rawslice)
                    s = self.parseData(rawslice)
                    self.lastRead = lastRead
                else:
                    # Cursor has been repositioned
                    s = '\r' + s
            self.__buffer.seek(pos)
            self.__buffer.truncate()
            self.__buffer.write(raw)

        self.__currentReadCo.X = cursorPos.X
        self.__currentReadCo.Y = cursorPos.Y

        return s
    
class ConsoleReaderSocket(ConsoleReaderBase): 
    
        
    def create_connection(self, **kwargs):
        try:        
            self.port = kwargs['port']
            # Create a TCP/IP socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('localhost', self.port)
            self.sock.bind(server_address)
            logger.info(f'Socket started at port: {self.port}')
            
            # Listen for incoming connections
            self.sock.listen(1)
            self.connection, client_address = self.sock.accept()
            self.connection.settimeout(.2)
            logger.info(f'Client connected: {client_address}')
        except:
            logger.error(f"Port: {self.port}")
            raise
            
    def close_connection(self):
        if self.connection:
            self.connection.close()
            
    def send_to_host(self, msg):
        # convert to bytes
        msg_bytes = str.encode(msg)
        self.connection.sendall(msg_bytes)
        
    def get_from_host(self):
        try:
            msg = self.connection.recv(4096)
        except socket.timeout as e:
            err = e.args[0]
            # this next if/else is a bit redundant, but illustrates how the
            # timeout exception is setup
            if err == 'timed out':
                logger.debug('recv timed out, retry later')
                return ''
            else:
                raise
        else:
            if len(msg) == 0:
                raise Exception('orderly shutdown on server end')
            else:
                # got a message do something :)
                return msg.decode()
    
    
class ConsoleReaderPipe(ConsoleReaderBase):
    def create_connection(self, **kwargs):
        pipe_name = 'wexpect_{}'.format(self.pid)
        pipe_full_path = r'\\.\pipe\{}'.format(pipe_name)
        logger.info('Start pipe server: %s', pipe_full_path)
        self.pipe = win32pipe.CreateNamedPipe(
            pipe_full_path,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            1, 65536, 65536, 0, None)
        logger.info("waiting for client")
        win32pipe.ConnectNamedPipe(self.pipe, None)
        logger.info('got client')
        
    def close_connection(self):
        if self.pipe:
            raise Exception(f'Unimplemented close')
        
    def send_to_host(self, msg):
        # convert to bytes
        msg_bytes = str.encode(msg)
        win32file.WriteFile(self.pipe, msg_bytes)
    
    def get_from_host(self):
        resp = win32file.ReadFile(self.pipe, 64*1024)
        ret = resp[1]
        return ret
        
         