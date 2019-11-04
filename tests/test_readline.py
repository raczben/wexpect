#!/usr/bin/env python
'''
MIT License

Copyright (c) 2008 Noah Spurrier, Richard Holden, Marco Molteni, Kimberley Burchett, Robert Stone,
Hartmut Goebel, Chad Schroeder, Erick Tryzelaar, Dave Kirby, Ids vander Molen, George Todd,
Noel Taylor, Nicolas D. Cesar, Alexander Gattin, Geoffrey Marshall, Francisco Lourenco, Glen Mabey,
Karthik Gurusamy, Fernando Perez, Corey Minyard, Jon Cohen, Guillaume Chazarain, Andrew Ryan,
Nick Craig-Wood, Andrew Stone, Jorgen Grahn, Benedek Racz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import wexpect
import time
import sys
import os
import unittest
from . import PexpectTestCase

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
        
        # Start the child process
        p = wexpect.spawn(fooPath)
        # Wait for prompt
        p.expect(prompt)
        
        p.sendline(str(num))
        for i in range(num +2): # +1 the line of sendline +1: Bye
            line = p.readline()
            self.assertEqual(expected_lines[i], line)
            
        # Start the child process
        p = wexpect.spawn(fooPath)
        # Wait for prompt
        p.expect(prompt)
        
        p.sendline(str(num))
        readlines_lines = p.readlines()
        self.assertEqual(expected_lines, readlines_lines)
        
            
if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ReadLineTestCase,'test')
