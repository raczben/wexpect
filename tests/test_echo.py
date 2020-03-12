import wexpect
import unittest
from tests import PexpectTestCase

class EchoTestCase(PexpectTestCase.PexpectTestCase):
    def testPath(self):
        # Path of cmd executable:
        cmd_exe = 'cmd'
        cmdPrompt = '>'

        # Start the child process
        p = wexpect.spawn(cmd_exe)

        # Wait for prompt
        p.expect(cmdPrompt)

        # Send a command
        p.sendline('echo hello')
        p.expect(cmdPrompt)
            
        self.assertEqual('hello', p.before.splitlines()[1])
            
if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(EchoTestCase,'test')
