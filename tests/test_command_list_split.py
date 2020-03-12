import wexpect
import unittest
from tests import PexpectTestCase

class TestCaseSplitCommandLine(PexpectTestCase.PexpectTestCase):
    def test_split_sizes(self):
        self.assertEqual(len(wexpect.split_command_line(r'')), 0)
        self.assertEqual(len(wexpect.split_command_line(r'one')), 1)
        self.assertEqual(len(wexpect.split_command_line(r'one two')), 2)
        self.assertEqual(len(wexpect.split_command_line(r'one  two')), 2)
        self.assertEqual(len(wexpect.split_command_line(r'one   two')), 2)
        self.assertEqual(len(wexpect.split_command_line(r'one^ one')), 1)
        self.assertEqual(len(wexpect.split_command_line('\'one one\'')), 1)
        self.assertEqual(len(wexpect.split_command_line(r'one\"one')), 1)
        self.assertEqual(len(wexpect.split_command_line(r"This^' is a^'^ test")), 3)
        
    def test_join_args(self):
        cmd = 'foo bar "b a z"'
        cmd2 = wexpect.join_args(wexpect.split_command_line(cmd))
        self.assertEqual(cmd2,  cmd)
        
        cmd = ['foo', 'bar', 'b a z']
        cmd2 = wexpect.split_command_line(wexpect.join_args(cmd))
        self.assertEqual(cmd2,  cmd)

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseSplitCommandLine,'test')
