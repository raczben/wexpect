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
import unittest
from . import PexpectTestCase

class InteractTestCase(PexpectTestCase.PexpectTestCase):
    def testPath(self):
        # Path of cmd executable:
        cmd_exe = 'cmd'
        cmdPrompt = '>'

        # Start the child process
        p = wexpect.spawn(cmd_exe)

        # Wait for prompt
        p.expect(cmdPrompt)
        
        p.interact()
        time.sleep(1)

        # Send a command
        p.sendline('echo hello')
        p.expect(cmdPrompt)
            
        self.assertEqual('hello', p.before.splitlines()[1])
            
if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(InteractTestCase,'test')
