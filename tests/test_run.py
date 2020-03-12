import wexpect
import unittest
import subprocess
import tempfile
import sys
import os
import re
from tests import PexpectTestCase

unicode_type = str


def timeout_callback(values):
    if values["event_count"] > 3:
        return 1
    return 0


def function_events_callback(values):
    try:
        previous_echoed = values["child_result_list"][-1]
        # lets pick up the line with valuable
        previous_echoed = previous_echoed.splitlines()[-3].strip()
        if previous_echoed.endswith("reserved."):
            return "echo stage-1\r\n"
        if previous_echoed.endswith("stage-1"):
            return "echo stage-2\r\n"
        elif previous_echoed.endswith("stage-2"):
            return "echo stage-3\r\n"
        elif previous_echoed.endswith("stage-3"):
            return "exit\r\n"
        else:
            raise Exception("Unexpected output {0}".format(previous_echoed))
    except IndexError:
        return "echo stage-1\r\n"


class RunFuncTestCase(PexpectTestCase.PexpectTestCase):
    runfunc = staticmethod(wexpect.run)
    cr = '\r'
    empty = ''
    prep_subprocess_out = staticmethod(lambda x: x)

    def test_run_exit(self):
        (data, exitstatus) = self.runfunc('python exit1.py', withexitstatus=1)
        assert exitstatus == 1, "Exit status of 'python exit1.py' should be 1."

    def test_run(self):
        the_old_way = subprocess.Popen(
            args=['uname', '-m', '-n'],
            stdout=subprocess.PIPE
        ).communicate()[0].rstrip()

        (the_new_way, exitstatus) = self.runfunc(
            'uname -m -n', withexitstatus=1)
        the_new_way = the_new_way.replace(self.cr, self.empty).rstrip()

        self.assertEqual(self.prep_subprocess_out(the_old_way).decode('utf-8'), the_new_way)
        self.assertEqual(exitstatus, 0)

    def test_run_callback(self):
        # TODO it seems like this test could block forever if run fails...
        events = {wexpect.TIMEOUT: timeout_callback}
        self.runfunc("cat", timeout=1, events=events)

    def test_run_bad_exitstatus(self):
        (the_new_way, exitstatus) = self.runfunc(
            'ls -l /najoeufhdnzkxjd', withexitstatus=1)
        self.assertNotEqual(exitstatus, 0)

    def test_run_event_as_string(self):
        re_flags =  re.DOTALL | re.MULTILINE
        events = {
            # second match on 'abc', echo 'def'
            re.compile('abc.*>', re_flags): 'echo "def"\r\n',
            # final match on 'def': exit
            re.compile('def.*>', re_flags): 'exit\r\n',
            # first match on 'GO:' prompt, echo 'abc'
            re.compile('Microsoft.*>', re_flags): 'echo "abc"\r\n'
            }

        (data, exitstatus) = wexpect.run(
            'cmd',
            withexitstatus=True,
            events=events,
            timeout=5)
        assert exitstatus == 0

    def test_run_event_as_function(self):
        events = {'>': function_events_callback}

        (data, exitstatus) = wexpect.run(
            'cmd',
            withexitstatus=True,
            events=events,
            timeout=10)
        assert exitstatus == 0

    # Unsupported
    # def test_run_event_as_method(self):
    #     events = {
    #         '>': RunFuncTestCase._method_events_callback
    #     }
    # 
    #     (data, exitstatus) = wexpect.run(
    #         'cmd',
    #         withexitstatus=True,
    #         events=events,
    #         timeout=10)
    #     assert exitstatus == 0

    def test_run_event_typeerror(self):
        events = {'>': -1}
        with self.assertRaises(TypeError):
            wexpect.run('cmd',
                        withexitstatus=True,
                        events=events,
                        timeout=10)

    def _method_events_callback(self, values):
        try:
            previous_echoed = (values["child_result_list"][-1].decode()
                               .split("\n")[-2].strip())
            if previous_echoed.endswith("foo1"):
                return "echo foo2\n"
            elif previous_echoed.endswith("foo2"):
                return "echo foo3\n"
            elif previous_echoed.endswith("foo3"):
                return "exit\n"
            else:
                raise Exception("Unexpected output {0!r}"
                                .format(previous_echoed))
        except IndexError:
            return "echo foo1\n"


if __name__ == '__main__':
    unittest.main()
