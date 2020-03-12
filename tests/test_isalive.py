import wexpect
import unittest
import signal
import sys
import time
from tests import PexpectTestCase

PYBIN = '"{}"'.format(sys.executable)

class IsAliveTestCase(PexpectTestCase.PexpectTestCase):
    """Various tests for the running status of processes."""

    def test_expect_wait(self):
        """Ensure consistency in wait() and isalive()."""
        p = wexpect.spawn('sleep 1')
        assert p.isalive()
        self.assertEqual(p.wait(), 0)
        assert not p.isalive()
        # In previous versions of ptyprocess/wexpect, calling wait() a second
        # time would raise an exception, but not since v4.0
        self.assertEqual(p.wait(), 0)

    def test_signal_wait(self):
        '''Test calling wait with a process terminated by a signal.'''
        if not hasattr(signal, 'SIGALRM'):
            return 'SKIP'
        p = wexpect.spawn(PYBIN, ['alarm_die.py'])
        p.wait()
        assert p.exitstatus is None
        self.assertEqual(p.signalstatus, signal.SIGALRM)

    def test_expect_isalive_dead_after_normal_termination (self):
        p = wexpect.spawn('ls', timeout=15)
        p.expect(wexpect.EOF)
        assert not p.isalive()

    def test_expect_isalive_dead_after_SIGHUP(self):
        p = wexpect.spawn('cat', timeout=5)
        assert p.isalive()
        self.assertTrue(p.terminate())
        p.expect(wexpect.EOF)
        assert not p.isalive()

    def test_expect_isalive_dead_after_SIGINT(self):
        p = wexpect.spawn('cat', timeout=5)
        assert p.isalive()
        force = False
        if sys.platform.lower().startswith('sunos'):
            # On Solaris (SmartOs), and only when executed from cron(1), SIGKILL
            # is required to end the sub-process. This is done using force=True
            force = True
        self.assertEqual(p.terminate(force), True)
        p.expect(wexpect.EOF)
        assert not p.isalive()

    def test_expect_isalive_dead_after_SIGKILL(self):
        p = wexpect.spawn('cat', timeout=5)
        assert p.isalive()
        p.kill()
        p.expect(wexpect.EOF)
        assert not p.isalive()

    def test_forced_terminate(self):
    
        p = wexpect.spawn(PYBIN + ' needs_kill.py')
        p.expect('READY')
        self.assertEqual(p.terminate(force=True), True)
        p.expect(wexpect.EOF)
        assert not p.isalive()

### Some platforms allow this. Some reset status after call to waitpid.
### probably not necessary, isalive() returns early when terminate is False.
    def test_expect_isalive_consistent_multiple_calls (self):
        '''This tests that multiple calls to isalive() return same value.
        '''
        p = wexpect.spawn('cat')
        assert p.isalive()
        assert p.isalive()
        p.sendeof()
        p.expect(wexpect.EOF)
        assert not p.isalive()
        assert not p.isalive()

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(IsAliveTestCase, 'test')
