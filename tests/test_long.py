#!/usr/bin/env python
'''
PEXPECT LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2012, Noah Spurrier <noah@noah.org>
    PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
    PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
    COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

'''
import wexpect
import unittest
import sys
import os
from . import PexpectTestCase
from . import long_printer

puskas_wiki = long_printer.puskas_wiki

class TestCaseLong(PexpectTestCase.PexpectTestCase):
    def test_long (self):
    
        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, here)

        # With quotes (C:\Program Files\Python37\python.exe needs quotes)
        python_executable = '"' + sys.executable + '" '
        child_script = here + '\\long_printer.py'


        longPrinter = python_executable + ' '  + child_script
        prompt = 'puskas> '
        
        # Start the child process
        p = wexpect.spawn(longPrinter)
        # Wait for prompt
        p.expect(prompt)
        
        for i in range(10):
            p.sendline('0')
            p.expect(prompt)
            self.assertEqual(p.before.splitlines()[1], puskas_wiki[0])
                
            p.sendline('all')
            p.expect(prompt)
            for a,b in zip(p.before.splitlines()[1:], puskas_wiki):
                self.assertEqual(a, b)
                    
            for j, paragraph in enumerate(puskas_wiki):
                p.sendline(str(j))
                p.expect(prompt)
                self.assertEqual(p.before.splitlines()[1], paragraph)
            

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseLong,'test')


        
