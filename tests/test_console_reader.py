import wexpect
import time
import unittest
import win32process
import win32api
import os
from tests import PexpectTestCase


if "RUN_CONSOLE_READER_TEST" not in os.environ:
    skip = True

class ConsoleReaderTestCase(PexpectTestCase.PexpectTestCase):

    @unittest.skipIf(skip, "Skipping test")
    def test_console_reader(self):
        
    
        pid = win32process.GetCurrentProcessId()
        tid = win32api.GetCurrentThreadId()
        args = ['sleep', '1']
        
        with self.assertRaises(SystemExit):
            wexpect.ConsoleReader(wexpect.join_args(args), tid=tid, pid=pid, cp=1250, logdir='wexpect')

        os.system('cls')
            
if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ConsoleReaderTestCase,'test')
