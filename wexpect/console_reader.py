import time
import sys
import logging
import os
import re
import shutil
import types
import traceback
import signal
import pkg_resources 
from io import StringIO

from ctypes import windll
import pywintypes
from win32com.shell.shell import SHGetSpecialFolderPath
import win32console
import win32process
import win32con
import win32gui
import win32api
import win32file
import winerror
import win32pipe
  
__version__ = 'test'

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

#
# Create logger: We write logs only to file. Printing out logs are dangerous, because of the deep
# console manipulation.
#
logger = logging.getLogger('wexpect')
os.environ['WEXPECT_LOGGER_LEVEL'] = 'DEBUG'
try:
    logger_level = os.environ['WEXPECT_LOGGER_LEVEL']
    logger.setLevel(logger_level)
    fh = logging.FileHandler('wexpect.log', 'w', 'utf-8')
    formatter = logging.Formatter('%(asctime)s - %(filename)s::%(funcName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
except KeyError:
    logger.setLevel(logging.ERROR)

# Test the logger
#logger.info('wexpect imported; logger working')


class ConsoleReader:
    """Consol class (aka. client-side python class) for the child.
    
    This class initialize the console starts the child in it and reads the console periodically.
    """

    def __init__(self, path, parent_pid, parent_tid, cp=None):
        """Initialize the console starts the child in it and reads the console periodically.

        

        Args:
            path (str): Child's executable with arguments.
            parent_pid (int): Parent (aka. host) process process-ID
            parent_tid (int): Parent (aka. host) process thread-ID
            cp (:obj:, optional): Output console code page.
        """
        self.lastRead  = 0
        self.__bufferY = 0
        self.lastReadData = ""
        self.totalRead = 0
        self.__buffer = StringIO()
        self.__currentReadCo = win32console.PyCOORDType(0, 0)
        
        
        logger.info("ConsoleReader started")
        logger.info("parent_tid %s" % parent_tid)
        self.create_pipe()
        if cp:
            try:
                logger.info("Setting console output code page to %s" % cp)
                win32console.SetConsoleOutputCP(cp)
                logger.info("Console output code page: %s" % windll.kernel32.GetConsoleOutputCP())
            except Exception as e:
                logger.info(e)
                
        try:
            logger.info('Spawning %s' % path)
            try:
                self.initConsole()
                
                time.sleep(1)
                si = win32process.GetStartupInfo()
                self.__childProcess, _, childPid, self.__tid = win32process.CreateProcess(None, path, None, None, False, 
                                                                             0, None, None, si)
                
                print('123')
                print('456')
                print('789')
                                                                             
            except Exception as e:
                logger.info(e)
                time.sleep(.1)
                return
            
            time.sleep(.1)
                  
            paused = False
            
   
            while True:
                consinfo = self.consout.GetConsoleScreenBufferInfo()
                cursorPos = consinfo['CursorPosition']
                
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
        except Exception as e:
            logger.error(e)
            time.sleep(.1)
            
    def create_pipe(self):
        pid = win32process.GetCurrentProcessId()
        pipe_name = 'wexpect_pipe_c2s_{}'.format(pid)
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
            
    def write_pipe(self, msg):
        # convert to bytes
        msg_bytes = str.encode(msg)
        win32file.WriteFile(self.pipe, msg_bytes)
            
    def initConsole(self, consout=None):
        if not consout:
            consout=self.getConsoleOut()
            
        rect = win32console.PySMALL_RECTType(0, 0, 79, 24)
        consout.SetConsoleWindowInfo(True, rect)
        size = win32console.PyCOORDType(80, 16000)
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
            # endCo.Y = endCo.Y+1
            # logger.info(endCo.Y+1)
            
        logger.info(startCo)
        logger.info(endCo)
        
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

        logger.info(repr(s))
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
        logger.debug(s)
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
        
        logger.debug('s: %r' % s)
        
        if s:
            lastReadData = self.lastReadData
            pos = self.getOffset(self.__currentReadCo)
            self.lastReadData = s
            if isSameY or not lastReadData.endswith('\r\n'):
                # Detect changed lines
                self.__buffer.seek(pos)
                buf = self.__buffer.read()
                logger.debug('buf: %r' % buf)
                logger.debug('raw: %r' % raw)
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
                logger.debug('s:   %r' % s)
            self.__buffer.seek(pos)
            self.__buffer.truncate()
            self.__buffer.write(raw)

        self.__currentReadCo.X = cursorPos.X
        self.__currentReadCo.Y = cursorPos.Y

        return s
    
    
def client(path, pid, tid):
    try:
        w = ConsoleReader(path, pid, tid)
        time.sleep(1)
        w.write_pipe(w.readConsoleToCursor())
    except Exception:
        tb = traceback.format_exc()
        logger.error(tb)
    
                
def pipe_client(conpid):
    pipe_name = 'wexpect_pipe_c2s_{}'.format(conpid)
    pipe_full_path = r'\\.\pipe\{}'.format(pipe_name)
    print('Trying to connect to pipe: {}'.format(pipe_full_path))
    quit = False

    while not quit:
        try:
            handle = win32file.CreateFile(
                pipe_full_path,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            res = win32pipe.SetNamedPipeHandleState(handle, win32pipe.PIPE_READMODE_MESSAGE, None, None)
            if res == 0:
                print(f"SetNamedPipeHandleState return code: {res}")
            while True:
                resp = win32file.ReadFile(handle, 64*1024)
                print(f"message: {resp}")
        except pywintypes.error as e:
            if e.args[0] == 2:
                print("no pipe, trying again in a bit")
                time.sleep(0.2)
            elif e.args[0] == 109:
                print("broken pipe, bye bye")
                quit = True


def main():
    pass
        
    
if __name__ == '__main__':

    si = win32process.GetStartupInfo()
    si.dwFlags = win32process.STARTF_USESHOWWINDOW
    si.wShowWindow = win32con.SW_HIDE
    pyargs = ['-c']
    
    dirname = os.path.dirname(sys.executable 
                              if getattr(sys, 'frozen', False) else 
                              os.path.abspath(__file__))
    
#    client('uname')
    
    pid = win32process.GetCurrentProcessId()
    tid = win32api.GetCurrentThreadId()
    
    commandLine = '"%s" %s "%s"' % (os.path.join(dirname, 'python.exe') 
                                    if getattr(sys, 'frozen', False) else 
                                    os.path.join(os.path.dirname(sys.executable), 'python.exe'), 
                                    ' '.join(pyargs), 
                                    "import sys;"
                                    "sys.path.append('D:\\\\bt\\\\wexpect');"
                                    "import console_reader;"
                                    "import time;"
                                    "console_reader.client('uname', {tid}, {pid});".format(pid=pid, tid=tid)
                                    )
                     
        
    print(commandLine)
    
    __oproc, _, conpid, __otid = win32process.CreateProcess(None, commandLine, None, None, False, 
                                                    win32process.CREATE_NEW_CONSOLE, None, None, si)
#    time.sleep(3)
    pipe_client(conpid)
   

    time.sleep(5)
        