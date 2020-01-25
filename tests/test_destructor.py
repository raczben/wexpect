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
from . import PexpectTestCase
import gc
import platform
import time

class TestCaseDestructor(PexpectTestCase.PexpectTestCase):
    def test_destructor (self):
        if platform.python_implementation() != 'CPython':
            # Details of garbage collection are different on other implementations
            return 'SKIP'
        gc.collect()
        time.sleep(2)
        p1 = wexpect.spawn('ls', port=4321)
        p2 = wexpect.spawn('ls', port=4322)
        p3 = wexpect.spawn('ls', port=4323)
        p4 = wexpect.spawn('ls', port=4324)
        p1.expect(wexpect.EOF)
        p2.expect(wexpect.EOF)
        p3.expect(wexpect.EOF)
        p4.expect(wexpect.EOF)
        p1.kill()
        p2.kill()
        p3.kill()
        p4.kill()
        p1 = None
        p2 = None
        p3 = None
        p4 = None
        gc.collect()
        time.sleep(2) # Some platforms are slow at gc... Solaris!
        

        p1 = wexpect.spawn('ls', port=4321)
        p2 = wexpect.spawn('ls', port=4322)
        p3 = wexpect.spawn('ls', port=4323)
        p4 = wexpect.spawn('ls', port=4324)
        p1.kill()
        p2.kill()
        p3.kill()
        p4.kill()
        del (p1)
        del (p2)
        del (p3)
        del (p4)
        gc.collect()
        time.sleep(2)

        p1 = wexpect.spawn('ls', port=4321)
        p2 = wexpect.spawn('ls', port=4322)
        p3 = wexpect.spawn('ls', port=4323)
        p4 = wexpect.spawn('ls', port=4324)


if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseDestructor,'test')

