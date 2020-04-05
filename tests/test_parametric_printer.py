import wexpect
import unittest
import sys
import os
import time
from tests import PexpectTestCase

class TestCaseParametricPrinter(PexpectTestCase.PexpectTestCase):
    def test_all_line_length (self):

        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, here)

        # With quotes (C:\Program Files\Python37\python.exe needs quotes)
        python_executable = '"' + sys.executable + '" '
        child_script = here + '\\parametric_printer.py'

        self.prompt = '> '

        # Start the child process
        self.p = wexpect.spawn(python_executable + ' '  + child_script)
        # Wait for prompt
        self.p.expect(self.prompt)

        self._test(['a'], range(1,200), [1], [0])

        self.p.terminate()

    def test_random(self):

        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, here)

        # With quotes (C:\Program Files\Python37\python.exe needs quotes)
        python_executable = '"' + sys.executable + '" '
        child_script = here + '\\parametric_printer.py'

        self.prompt = '> '

        # Start the child process
        self.p = wexpect.spawn(python_executable + ' '  + child_script)
        # Wait for prompt
        self.p.expect(self.prompt)

        self._test(['a', 'b', 'c'], [1, 2, 4, 8], [1, 2, 4, 8], [-1, 0, 1, 2])
        self._test(['a', 'b', 'c'], [16], [16], [-1, 0, 1])
        self._test(['a', 'b', 'c'], [16, 32, 64], [16, 32, 64], [-1, 0])

        self.p.terminate()

    @unittest.skipIf(wexpect.spawn_class_name == 'legacy_wexpect', "legacy has bug around refreshing long consoles")
    def test_long_console(self):

        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, here)

        # With quotes (C:\Program Files\Python37\python.exe needs quotes)
        python_executable = '"' + sys.executable + '" '
        child_script = here + '\\parametric_printer.py'

        self.prompt = '> '

        # Start the child process
        self.p = wexpect.spawn(python_executable + ' '  + child_script)
        # Wait for prompt
        self.p.expect(self.prompt)

        self._test(['a', 'b', 'c', 'd', 'e', 'f'], [8, 16, 32, 64], [64, 128, 256], [-1, 0])

        self.p.terminate()

    def _test(self, character_list, character_count_list, line_count_list, speed_ms_list):

        # print(f'character_list: {character_list}  character_count_list: {character_count_list}  line_count_list: {line_count_list}  speed_ms_list: {speed_ms_list}')
        for character in character_list:
            for character_count in character_count_list:
                for line_count in line_count_list:
                    for speed_ms in speed_ms_list:
                        command = f'{character},{character_count},{line_count},{speed_ms}'
                        self.p.sendline(command)
                        self.p.expect(self.prompt)
                        expected = [character*character_count] * line_count
                        try:
                            self.assertEqual(self.p.before.splitlines()[1:-1], expected)
                        except:
                            raise

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseParametricPrinter,'test')
