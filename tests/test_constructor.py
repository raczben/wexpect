import wexpect
import unittest
import time
from tests import PexpectTestCase

class TestCaseConstructor(PexpectTestCase.PexpectTestCase):
    def test_constructor (self):
        '''This tests that the constructor will work and give
        the same results for different styles of invoking __init__().
        This assumes that the root directory / is static during the test.
        '''
        p1 = wexpect.spawn('uname -m -n -p -r -s -v', timeout=5)
        p1.expect(wexpect.EOF)
        time.sleep(p1.delayafterterminate)
        p2 = wexpect.spawn('uname', ['-m', '-n', '-p', '-r', '-s', '-v'], timeout=5)
        p2.expect(wexpect.EOF)
        time.sleep(p1.delayafterterminate)
        self.assertEqual(p1.before, p2.before)
        self.assertEqual(str(p1).splitlines()[1:9], str(p2).splitlines()[1:9])
        
        run_result = wexpect.run('uname -m -n -p -r -s -v')
        self.assertEqual(run_result, p2.before)

    def test_named_parameters (self):
        '''This tests that named parameters work.
        '''
        p = wexpect.spawn('ls',timeout=10)
        p.wait()
        p = wexpect.spawn(timeout=10, command='ls')
        p.wait()
        p = wexpect.spawn(args=[], command='ls')
        p.wait()

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseConstructor,'test')
