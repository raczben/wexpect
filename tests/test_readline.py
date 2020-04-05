import wexpect
import time
import sys
import os
import unittest
from tests import PexpectTestCase

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)

print(wexpect.__version__)

# With quotes (C:\Program Files\Python37\python.exe needs quotes)
python_executable = '"' + sys.executable + '" '
child_script = here + '\\lines_printer.py'

class ReadLineTestCase(PexpectTestCase.PexpectTestCase):
    def testReadline(self):
        fooPath = python_executable + ' '  + child_script
        prompt = ': '
        num = 5

        # Start the child process
        p = wexpect.spawn(fooPath)
        # Wait for prompt
        p.expect(prompt)
        p.sendline(str(num))
        p.expect('Bye!\r\n')
        expected_lines = p.before.splitlines(True) # Keep the line end
        expected_lines += [p.match.group()]

        # Termination of the SpawnSocket is slow. We have to wait to prevent the failure of the next test.
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.wait()

        # Start the child process
        p = wexpect.spawn(fooPath)
        # Wait for prompt
        p.expect(prompt)

        p.sendline(str(num))
        for i in range(num +2): # +1 the line of sendline +1: Bye
            line = p.readline()
            self.assertEqual(expected_lines[i], line)

        # Termination of the SpawnSocket is slow. We have to wait to prevent the failure of the next test.
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.wait()

        # Start the child process
        p = wexpect.spawn(fooPath)
        # Wait for prompt
        p.expect(prompt)

        p.sendline(str(num))
        readlines_lines = p.readlines()
        self.assertEqual(expected_lines, readlines_lines)

        # Termination of the SpawnSocket is slow. We have to wait to prevent the failure of the next test.
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.wait()


if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ReadLineTestCase,'test')
