from __future__ import print_function

import contextlib
import unittest
import signal
import sys
import os


class PexpectTestCase(unittest.TestCase):
    def setUp(self):
        self.PYTHONBIN = sys.executable
        self.original_path = os.getcwd()
        tests_dir = os.path.dirname(__file__)
        self.project_dir = project_dir = os.path.dirname(tests_dir)

        # all tests are executed in this folder; there are many auxiliary
        # programs in this folder executed by spawn().
        os.chdir(tests_dir)

        # If the pexpect raises an exception after fork(), but before
        # exec(), our test runner *also* forks.  We prevent this by
        # storing our pid and asserting equality on tearDown.
        self.pid = os.getpid()

        coverage_rc = os.path.join(project_dir, '.coveragerc')
        os.environ['COVERAGE_PROCESS_START'] = coverage_rc
        os.environ['COVERAGE_FILE'] = os.path.join(project_dir, '.coverage')
        print('\n', self.id(), end=' ')
        sys.stdout.flush()

        # some build agents will ignore SIGHUP and SIGINT, which python
        # inherits.  This causes some of the tests related to terminate()
        # to fail.  We set them to the default handlers that they should
        # be, and restore them back to their SIG_IGN value on tearDown.
        #
        # I'm not entirely convinced they need to be restored, only our
        # test runner is affected.
        self.restore_ignored_signals = [
            value for value in (signal.SIGINT,)
            if signal.getsignal(value) == signal.SIG_IGN]
        if signal.SIGINT in self.restore_ignored_signals:
            # SIGINT should be set to signal.default_int_handler
            signal.signal(signal.SIGINT, signal.default_int_handler)
        unittest.TestCase.setUp(self)

    def tearDown(self):
        # restore original working folder
        os.chdir(self.original_path)

        if self.pid != os.getpid():
            # The build server pattern-matches phrase 'Test runner has forked!'
            print("Test runner has forked! This means a child process raised "
                  "an exception before exec() in a test case, the error is "
                  "more than likely found above this line in stderr.",
                  file=sys.stderr)
            exit(1)

        # restore signal handlers
        for signal_value in self.restore_ignored_signals:
            signal.signal(signal_value, signal.SIG_IGN)

    if sys.version_info < (2, 7):
        # We want to use these methods, which are new/improved in 2.7, but
        # we are still supporting 2.6 for the moment. This section can be
        # removed when we drop Python 2.6 support.
        @contextlib.contextmanager
        def assertRaises(self, excClass):
            try:
                yield
            except Exception as e:
                assert isinstance(e, excClass)
            else:
                raise AssertionError("%s was not raised" % excClass)

        @contextlib.contextmanager
        def assertRaisesRegexp(self, excClass, pattern):
            import re
            try:
                yield
            except Exception as e:
                assert isinstance(e, excClass)
                assert re.match(pattern, str(e))
            else:
                raise AssertionError("%s was not raised" % excClass)
