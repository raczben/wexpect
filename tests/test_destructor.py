import wexpect
import unittest
from tests import PexpectTestCase
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
