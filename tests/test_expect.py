import multiprocessing
import unittest
import subprocess
import time
import signal
import sys
import os

import wexpect
from tests import PexpectTestCase

# Many of these test cases blindly assume that sequential directory
# listings of the /bin directory will yield the same results.
# This may not be true, but seems adequate for testing now.
# I should fix this at some point.

PYTHONBINQUOTE = '"{}"'.format(sys.executable)
FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
def hex_dump(src, length=16):
    result=[]
    for i in range(0, len(src), length):
       s = src[i:i+length]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       printable = s.translate(FILTER)
       result.append("%04X   %-*s   %s\n" % (i, length*3, hexa, printable))
    return ''.join(result)

def hex_diff(left, right):
        diff = ['< %s\n> %s' % (_left, _right,) for _left, _right in zip(
            hex_dump(left).splitlines(), hex_dump(right).splitlines())
            if _left != _right]
        return '\n' + '\n'.join(diff,)


class ExpectTestCase (PexpectTestCase.PexpectTestCase):

    def test_expect_basic (self):
        p = wexpect.spawn('cat', timeout=5)
        p.sendline ('Hello')
        p.sendline ('there')
        p.sendline ('Mr. Python')
        p.expect ('Hello')
        p.expect ('there')
        p.expect ('Mr. Python')
        p.sendeof ()
        p.expect (wexpect.EOF)

    def test_expect_exact_basic (self):
        p = wexpect.spawn('cat', timeout=5)
        p.sendline ('Hello')
        p.sendline ('there')
        p.sendline ('Mr. Python')
        p.expect_exact ('Hello')
        p.expect_exact ('there')
        p.expect_exact ('Mr. Python')
        p.sendeof ()
        p.expect_exact (wexpect.EOF)

    def test_expect_ignore_case(self):
        '''This test that the ignorecase flag will match patterns
        even if case is different using the regex (?i) directive.
        '''
        p = wexpect.spawn('cat', timeout=5)
        p.sendline ('HELLO')
        p.sendline ('there')
        p.expect ('(?i)hello')
        p.expect ('(?i)THERE')
        p.sendeof ()
        p.expect (wexpect.EOF)

    def test_expect_ignore_case_flag(self):
        '''This test that the ignorecase flag will match patterns
        even if case is different using the ignorecase flag.
        '''
        p = wexpect.spawn('cat', timeout=5)
        p.ignorecase = True
        p.sendline ('HELLO')
        p.sendline ('there')
        p.expect ('hello')
        p.expect ('THERE')
        p.sendeof ()
        p.expect (wexpect.EOF)

    def test_expect_order (self):
        '''This tests that patterns are matched in the same order as given in the pattern_list.

        (Or does it?  Doesn't it also pass if expect() always chooses
        (one of the) the leftmost matches in the input? -- grahn)
        ... agreed! -jquast, the buffer ptr isn't forwarded on match, see first two test cases
        '''
        p = wexpect.spawn('cat', timeout=5, echo=True)
        self._expect_order(p)

    def test_expect_order_exact (self):
        '''Like test_expect_order(), but using expect_exact().
        '''
        p = wexpect.spawn('cat', timeout=5, echo=True)
        p.expect = p.expect_exact
        self._expect_order(p)

    def _expect_order (self, p):
        p.sendline ('1234')
        p.sendline ('abcd')
        p.sendline ('wxyz')
        p.sendline ('7890')
        p.sendeof ()
        for _ in range(2):
            index = p.expect ([
                '1234',
                'abcd',
                'wxyz',
                wexpect.EOF,
                '7890' ])
            self.assertEqual(index,  0, (index, p.before, p.after))

        for _ in range(2):
            index = p.expect ([
                '54321',
                wexpect.TIMEOUT,
                '1234',
                'abcd',
                'wxyz',
                wexpect.EOF], timeout=5)
            self.assertEqual(index,  3, (index, p.before, p.after))

        for _ in range(2):
            index = p.expect ([
                '54321',
                wexpect.TIMEOUT,
                '1234',
                'abcd',
                'wxyz',
                wexpect.EOF], timeout=5)
            self.assertEqual(index,  4, (index, p.before, p.after))

        for _ in range(2):
            index = p.expect ([
                wexpect.EOF,
                'abcd',
                'wxyz',
                '7890' ])
            self.assertEqual(index,  3, (index, p.before, p.after))

        index = p.expect ([
            'abcd',
            'wxyz',
            '7890',
            wexpect.EOF])
        self.assertEqual(index,  3, (index, p.before, p.after))

        # Termination of the SpawnSocket is slow. We have to wait to prevent the failure of the next test.
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.wait()

    def test_expect_index (self):
        '''This tests that mixed list of regex strings, TIMEOUT, and EOF all
        return the correct index when matched.
        '''
        p = wexpect.spawn('cat', timeout=5, echo=False)
        self._expect_index(p)

    def test_expect_index_exact (self):
        '''Like test_expect_index(), but using expect_exact().
        '''
        p = wexpect.spawn('cat', timeout=5, echo=False)
        p.expect = p.expect_exact
        self._expect_index(p)
        # Termination of the SpawnSocket is slow. We have to wait to prevent the failure of the next test.
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.wait()

    def _expect_index (self, p):
        p.sendline ('1234')
        index = p.expect (['abcd','wxyz','1234',wexpect.EOF])
        self.assertEqual(index,  2, "index="+str(index))
        p.sendline ('abcd')
        index = p.expect ([wexpect.TIMEOUT,'abcd','wxyz','1234',wexpect.EOF])
        self.assertEqual(index,  1, "index="+str(index))
        p.sendline ('wxyz')
        index = p.expect (['54321',wexpect.TIMEOUT,'abcd','wxyz','1234',wexpect.EOF])
        self.assertEqual(index,  3, "index="+str(index)) # Expect 'wxyz'
        p.sendline ('$*!@?')
        index = p.expect (['54321',wexpect.TIMEOUT,'abcd','wxyz','1234',wexpect.EOF],
                          timeout=1)
        self.assertEqual(index,  1, "index="+str(index)) # Expect TIMEOUT
        p.sendeof ()
        index = p.expect (['54321',wexpect.TIMEOUT,'abcd','wxyz','1234',wexpect.EOF])
        self.assertEqual(index,  5, "index="+str(index)) # Expect EOF

    def test_expect (self):
        the_old_way = subprocess.Popen(args=['ls', '-l'],
                stdout=subprocess.PIPE).communicate()[0].rstrip()
        p = wexpect.spawn('ls -l')
        the_new_way = ''
        while 1:
            i = p.expect (['\n', wexpect.EOF])
            the_new_way = the_new_way + p.before
            if i == 1:
                break
        the_new_way = the_new_way.rstrip()
        the_new_way = the_new_way.replace('\r\n', '\n'
                ).replace('\r', '\n').replace('\n\n', '\n').rstrip()
        the_old_way = the_old_way.decode('utf-8')
        the_old_way = the_old_way.replace('\r\n', '\n'
                ).replace('\r', '\n').replace('\n\n', '\n').rstrip()
        # print(repr(the_old_way))
        # print(repr(the_new_way))
        # the_old_way = the_old_way[0:10000]
        # the_new_way = the_new_way[0:10000]
        self.assertEqual(the_old_way,  the_new_way)

    def test_expect_exact (self):
        the_old_way = subprocess.Popen(args=['ls', '-l'],
                stdout=subprocess.PIPE).communicate()[0].rstrip()
        p = wexpect.spawn('ls -l')
        the_new_way = ''
        while 1:
            i = p.expect_exact (['\n', wexpect.EOF])
            the_new_way = the_new_way + p.before
            if i == 1:
                break
        the_new_way = the_new_way.replace('\r\n', '\n'
                ).replace('\r', '\n').replace('\n\n', '\n').rstrip()
        the_old_way = the_old_way.decode('utf-8')
        the_old_way = the_old_way.replace('\r\n', '\n'
                ).replace('\r', '\n').replace('\n\n', '\n').rstrip()
        self.assertEqual(the_old_way,  the_new_way)
        # Termination of the SpawnSocket is slow. We have to wait to prevent the failure of the next test.
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.wait()

        p = wexpect.spawn('echo hello.?world')
        i = p.expect_exact('.?')
        self.assertEqual(p.before, 'hello')
        self.assertEqual(p.after, '.?')

    def test_expect_eof (self):
        the_old_way = subprocess.Popen(args=['ls', '-l'],
                stdout=subprocess.PIPE).communicate()[0].rstrip()
        p = wexpect.spawn('ls -l')
        p.expect(wexpect.EOF) # This basically tells it to read everything. Same as wexpect.run() function.
        the_new_way = p.before
        the_new_way = the_new_way.replace('\r\n', '\n'
                ).replace('\r', '\n').replace('\n\n', '\n').rstrip()
        the_old_way = the_old_way.decode('utf-8')
        the_old_way = the_old_way.replace('\r\n', '\n'
                ).replace('\r', '\n').replace('\n\n', '\n').rstrip()
        self.assertEqual(the_old_way,  the_new_way)

        # Termination of the SpawnSocket is slow. We have to wait to prevent the failure of the next test.
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.wait()

    def test_expect_timeout (self):
        p = wexpect.spawn('cat', timeout=5)
        p.expect(wexpect.TIMEOUT) # This tells it to wait for timeout.
        self.assertEqual(p.after, wexpect.TIMEOUT)

    def test_unexpected_eof (self):
        p = wexpect.spawn('ls -l /bin')
        try:
            p.expect('_Z_XY_XZ') # Probably never see this in ls output.
        except wexpect.EOF:
            pass
        else:
            self.fail ('Expected an EOF exception.')

        if wexpect.spawn_class_name == 'SpawnSocket':
            p.wait()

    def test_buffer_interface(self):
        p = wexpect.spawn('cat', timeout=5)
        p.sendline ('Hello')
        p.expect ('Hello')
        assert len(p.buffer)
        p.buffer = 'Testing'
        p.sendeof ()
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.wait()

    def _before_after(self, p):
        p.timeout = 5

        p.expect('5')
        self.assertEqual(p.after, '5')
        self.assertTrue(p.before.startswith('[0, 1, 2'), p.before)

        p.expect('50')
        self.assertEqual(p.after, '50')
        self.assertTrue(p.before.startswith(', 6, 7, 8'), p.before[:20])
        self.assertTrue(p.before.endswith('48, 49, '), p.before[-20:])

        p.expect(wexpect.EOF)
        self.assertEqual(p.after, wexpect.EOF)
        assert p.before.startswith(', 51, 52'), p.before[:20]
        assert p.before.endswith(', 99]\r\n'), p.before[-20:]

        if wexpect.spawn_class_name == 'SpawnSocket':
            p.wait()

    def test_before_after(self):
        '''This tests expect() for some simple before/after things.
        '''
        p = wexpect.spawn('%s -Wi list100.py' % PYTHONBINQUOTE)
        self._before_after(p)

    def test_before_after_exact(self):
        '''This tests some simple before/after things, for
        expect_exact(). (Grahn broke it at one point.)
        '''
        p = wexpect.spawn('%s -Wi list100.py' % PYTHONBINQUOTE)
        # mangle the spawn so we test expect_exact() instead
        p.expect = p.expect_exact
        self._before_after(p)

    def _ordering(self, p):
        p.timeout = 20
        p.expect('>>> ')

        p.sendline('list(range(4*3))')
        self.assertEqual(p.expect(['5,', '5,']), 0)
        p.expect('>>> ')

        p.sendline('list(range(4*3))')
        self.assertEqual(p.expect(['7,', '5,']), 1)
        p.expect('>>> ')

        p.sendline('list(range(4*3))')
        self.assertEqual(p.expect(['5,', '7,']), 0)
        p.expect('>>> ')

        p.sendline('list(range(4*5))')
        self.assertEqual(p.expect(['2,', '12,']), 0)
        p.expect('>>> ')

        p.sendline('list(range(4*5))')
        self.assertEqual(p.expect(['12,', '2,']), 1)

        p.sendline('exit()')

    def test_ordering(self):
        '''This tests expect() for which pattern is returned
        when many may eventually match. I (Grahn) am a bit
        confused about what should happen, but this test passes
        with wexpect 2.1.
        '''
        p = wexpect.spawn(PYTHONBINQUOTE)
        self._ordering(p)

    def test_ordering_exact(self):
        '''This tests expect_exact() for which pattern is returned
        when many may eventually match. I (Grahn) am a bit
        confused about what should happen, but this test passes
        for the expect() method with wexpect 2.1.
        '''
        p = wexpect.spawn(PYTHONBINQUOTE)
        # mangle the spawn so we test expect_exact() instead
        p.expect = p.expect_exact
        self._ordering(p)

        # Termination of the SpawnSocket is slow. We have to wait to prevent the failure of the next test.
        if wexpect.spawn_class_name == 'SpawnSocket':
            p.wait()

    def _greed(self, expect):
        # End at the same point: the one with the earliest start should win
        self.assertEqual(expect(['3, 4', '2, 3, 4']), 1)

        # Start at the same point: first pattern passed wins
        self.assertEqual(expect(['5,', '5, 6']), 0)

        # Same pattern passed twice: first instance wins
        self.assertEqual(expect(['7, 8', '7, 8, 9', '7, 8']), 0)

    def _greed_read1(self, expect):
        # Here, one has an earlier start and a later end. When processing
        # one character at a time, the one that finishes first should win,
        # because we don't know about the other match when it wins.
        # If maxread > 1, this behaviour is currently undefined, although in
        # most cases the one that starts first will win.
        self.assertEqual(expect(['1, 2, 3', '2,']), 1)

    def test_greed(self):
        p = wexpect.spawn(PYTHONBINQUOTE + ' list100.py')
        self._greed(p.expect)

    def test_greed_exact(self):
        p = wexpect.spawn(PYTHONBINQUOTE + ' list100.py')
        self._greed(p.expect_exact)

    def test_bad_arg(self):
        p = wexpect.spawn('cat')
        with self.assertRaisesRegex(TypeError, '.*must be one of'):
            p.expect(1)
        with self.assertRaisesRegex(TypeError, '.*must be one of'):
            p.expect([1, '2'])
        with self.assertRaisesRegex(TypeError, '.*must be one of'):
            p.expect_exact(1)
        with self.assertRaisesRegex(TypeError, '.*must be one of'):
            p.expect_exact([1, '2'])

    def test_timeout_none(self):
        p = wexpect.spawn('echo abcdef', timeout=None)
        p.expect('abc')
        p.expect_exact('def')
        p.expect(wexpect.EOF)

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ExpectTestCase, 'test')
