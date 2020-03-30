import unittest
import sys
import re
import os
import time

import wexpect
from tests import PexpectTestCase

# the program cat(1) may display ^D\x08\x08 when \x04 (EOF, Ctrl-D) is sent
_CAT_EOF = '^D\x08\x08'

def _u(s):
    return s

PYBIN = '"{}"'.format(sys.executable)

class TestCaseMisc(PexpectTestCase.PexpectTestCase):

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_isatty(self):
        " Test isatty() is True after spawning process on most platforms. "
        child = wexpect.spawn('cat', coverage_console_reader=True)
        if not child.isatty() and sys.platform.lower().startswith('sunos'):
            if hasattr(unittest, 'SkipTest'):
                raise unittest.SkipTest("Not supported on this platform.")
            return 'skip'
        assert child.isatty()

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_read(self):
        " Test spawn.read by calls of various size. "
        child = wexpect.spawn('cat', coverage_console_reader=True)
        child.sendline("abc")
        child.sendeof()
        child.readline()
        self.assertEqual(child.read(0), '')
        self.assertEqual(child.read(1), 'a')
        self.assertEqual(child.read(1), 'b')
        self.assertEqual(child.read(1), 'c')
        self.assertEqual(child.read(2), '\r\n')

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_readline_bin_echo(self):
        " Test spawn('echo'). "
        # given,
        child = wexpect.spawn('echo', ['alpha', 'beta'], coverage_console_reader=True)

        # exercise,
        self.assertEqual(child.readline(), 'alpha beta\r\n')

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_readline(self):
        " Test spawn.readline(). "
        # when argument 0 is sent, nothing is returned.
        # Otherwise the argument value is meaningless.
        child = wexpect.spawn('cat', coverage_console_reader=True)
        child.sendline("alpha")
        child.sendline("beta")
        child.sendline("gamma")
        child.sendline("delta")
        child.sendeof()
        self.assertEqual(child.readline(0), '')
        child.readline().rstrip()
        self.assertEqual(child.readline().rstrip(), 'alpha')
        child.readline().rstrip()
        self.assertEqual(child.readline(1).rstrip(), 'beta')
        child.readline().rstrip()
        self.assertEqual(child.readline(2).rstrip(), 'gamma')
        child.readline().rstrip()
        self.assertEqual(child.readline().rstrip(), 'delta')
        child.expect(wexpect.EOF)
        if type(child).__name__ in ['SpawnPipe', 'SpawnSocket']:
            time.sleep(child.delayafterterminate)
            assert not child.isalive(trust_console=False)
        else:
            assert not child.isalive()
        self.assertEqual(child.exitstatus, 0)

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_iter(self):
        " iterating over lines of spawn.__iter__(). "
        child = wexpect.spawn('echo "abc\r\n123"', coverage_console_reader=True)
        # Don't use ''.join() because we want to test __iter__().
        page = ''
        for line in child:
            page += line
        page = page.replace(_CAT_EOF, '')
        self.assertEqual(page, 'abc\r\n123\r\n')

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_readlines(self):
        " reading all lines of spawn.readlines(). "
        child = wexpect.spawn('cat', echo=False, coverage_console_reader=True)
        child.sendline("abc")
        child.sendline("123")
        child.sendeof()
        page = ''.join(child.readlines()).replace(_CAT_EOF, '')
        self.assertEqual(page, '\r\nabc\r\n\r\n123\r\n')
        child.expect(wexpect.EOF)
        if type(child).__name__ in ['SpawnPipe', 'SpawnSocket']:
            time.sleep(child.delayafterterminate)
            assert not child.isalive(trust_console=False)
        else:
            assert not child.isalive()
        self.assertEqual(child.exitstatus, 0)

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_write(self):
        " write a character and return it in return. "
        child = wexpect.spawn('cat', coverage_console_reader=True)
        child.write('a')
        child.write('\r')
        child.readline()
        self.assertEqual(child.readline(), 'a\r\n')

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_writelines(self):
        " spawn.writelines() "
        child = wexpect.spawn('cat', coverage_console_reader=True)
        # notice that much like file.writelines, we do not delimit by newline
        # -- it is equivalent to calling write(''.join([args,]))
        child.writelines(['abc', '123', 'xyz', '\r'])
        child.sendeof()
        child.readline()
        line = child.readline()
        self.assertEqual(line, 'abc123xyz\r\n')

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_eof(self):
        " call to expect() after EOF is received raises wexpect.EOF "
        child = wexpect.spawn('cat', coverage_console_reader=True)
        child.sendeof()
        with self.assertRaises(wexpect.EOF):
            child.expect('the unexpected')

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_with(self):
        "spawn can be used as a context manager"
        with wexpect.spawn(PYBIN + ' echo_w_prompt.py', coverage_console_reader=True) as p:
            p.expect('<in >')
            p.sendline('alpha')
            p.expect('<out>alpha')
            assert p.isalive()

        assert not p.isalive()

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_terminate(self):
        " test force terminate always succeeds (SIGKILL). "
        child = wexpect.spawn('cat', coverage_console_reader=True)
        child.terminate(force=1)
        assert child.terminated

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_bad_arguments_suggest_fdpsawn(self):
        " assert custom exception for spawn(int). "
        expect_errmsg = "maybe you want to use fdpexpect.fdspawn"
        with self.assertRaisesRegex(wexpect.ExceptionPexpect,
                                     ".*" + expect_errmsg):
            wexpect.spawn(1, coverage_console_reader=True)

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_bad_arguments_second_arg_is_list(self):
        " Second argument to spawn, if used, must be only a list."
        with self.assertRaises(TypeError):
            wexpect.spawn('ls', '-la', coverage_console_reader=True)

        with self.assertRaises(TypeError):
            # not even a tuple,
            wexpect.spawn('ls', ('-la',), coverage_console_reader=True)

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_read_after_close_raises_value_error(self):
        " Calling read_nonblocking after close raises ValueError. "
        # as read_nonblocking underlies all other calls to read,
        # ValueError should be thrown for all forms of read.
        with self.assertRaises(ValueError):
            p = wexpect.spawn('cat', coverage_console_reader=True)
            p.close()
            p.read_nonblocking()

        with self.assertRaises(ValueError):
            p = wexpect.spawn('cat', coverage_console_reader=True)
            p.close()
            p.read()

        with self.assertRaises(ValueError):
            p = wexpect.spawn('cat', coverage_console_reader=True)
            p.close()
            p.readline()

        with self.assertRaises(ValueError):
            p = wexpect.spawn('cat', coverage_console_reader=True)
            p.close()
            p.readlines()

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_isalive(self):
        " check isalive() before and after EOF. (True, False) "
        child = wexpect.spawn('cat', coverage_console_reader=True)
        self.assertTrue(child.isalive())
        child.sendeof()
        child.expect(wexpect.EOF)
        assert child.isalive() is False
        self.assertFalse(child.isalive())

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_bad_type_in_expect(self):
        " expect() does not accept dictionary arguments. "
        child = wexpect.spawn('cat', coverage_console_reader=True)
        with self.assertRaises(TypeError):
            child.expect({})

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_cwd(self):
        " check keyword argument `cwd=' of wexpect.run() "
        try:
            os.mkdir('cwd_tmp')
        except:
            pass
        tmp_dir = os.path.realpath('cwd_tmp')
        child = wexpect.spawn('cmd', coverage_console_reader=True)
        child.expect('>')
        child.sendline('cd')
        child.expect('>')
        default = child.before.splitlines()[1]
        child.terminate()
        child = wexpect.spawn('cmd', cwd=tmp_dir, coverage_console_reader=True)
        child.expect('>')
        child.sendline('cd')
        child.expect('>')
        pwd_tmp = child.before.splitlines()[1]
        child.terminate()
        self.assertNotEqual(default, pwd_tmp)
        self.assertEqual(tmp_dir, _u(pwd_tmp))

    def _test_searcher_as(self, searcher, plus=None):
        # given,
        given_words = ['alpha', 'beta', 'gamma', 'delta', ]
        given_search = given_words
        if searcher == wexpect.searcher_re:
            given_search = [re.compile(word) for word in given_words]
        if plus is not None:
            given_search = given_search + [plus]
        search_string = searcher(given_search)
        basic_fmt = '\n    {0}: {1}'
        fmt = basic_fmt
        if searcher is wexpect.searcher_re:
            fmt = '\n    {0}: re.compile({1})'
        expected_output = '{0}:'.format(searcher.__name__)
        idx = 0
        for word in given_words:
            expected_output += fmt.format(idx, '"{0}"'.format(word))
            idx += 1
        if plus is not None:
            if plus == wexpect.EOF:
                expected_output += basic_fmt.format(idx, 'EOF')
            elif plus == wexpect.TIMEOUT:
                expected_output += basic_fmt.format(idx, 'TIMEOUT')

        # exercise,
        self.assertEqual(search_string.__str__(), expected_output)

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_searcher_as_string(self):
        " check searcher_string(..).__str__() "
        self._test_searcher_as(wexpect.searcher_string)

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_searcher_as_string_with_EOF(self):
        " check searcher_string(..).__str__() that includes EOF "
        self._test_searcher_as(wexpect.searcher_string, plus=wexpect.EOF)

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_searcher_as_string_with_TIMEOUT(self):
        " check searcher_string(..).__str__() that includes TIMEOUT "
        self._test_searcher_as(wexpect.searcher_string, plus=wexpect.TIMEOUT)

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_searcher_re_as_string(self):
        " check searcher_re(..).__str__() "
        self._test_searcher_as(wexpect.searcher_re)

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_searcher_re_as_string_with_EOF(self):
        " check searcher_re(..).__str__() that includes EOF "
        self._test_searcher_as(wexpect.searcher_re, plus=wexpect.EOF)

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_searcher_re_as_string_with_TIMEOUT(self):
        " check searcher_re(..).__str__() that includes TIMEOUT "
        self._test_searcher_as(wexpect.searcher_re, plus=wexpect.TIMEOUT)

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy unsupported")
    def test_exception_tb(self):
        " test get_trace() filters away wexpect/__init__.py calls. "
        p = wexpect.spawn('sleep 1', coverage_console_reader=True)
        try:
            p.expect('BLAH')
        except wexpect.ExceptionPexpect as e:
            # get_trace should filter out frames in wexpect's own code
            tb = e.get_trace()
            # exercise,
            assert 'raise ' not in tb
            assert 'wexpect/__init__.py' not in tb
        else:
            assert False, "Should have raised an exception."

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseMisc,'test')
