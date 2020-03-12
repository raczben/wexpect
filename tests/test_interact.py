import wexpect
import time
import unittest
from tests import PexpectTestCase

class InteractTestCase(PexpectTestCase.PexpectTestCase):

    @unittest.skipIf(not (hasattr(wexpect, 'legacy_wexpect')) or (hasattr(wexpect.spawn, 'interact')), "spawn does not support runtime interact switching.")
    def test_interact(self):
        # Path of cmd executable:
        cmd_exe = 'cmd'
        cmdPrompt = '>'

        # Start the child process
        p = wexpect.spawn(cmd_exe)

        # Wait for prompt
        p.expect(cmdPrompt)
        
        p.interact()
        time.sleep(1)

        # Send a command
        p.sendline('echo hello')
        p.expect(cmdPrompt)
        
        p.stop_interact()
            
        self.assertEqual('hello', p.before.splitlines()[1])
    
    @unittest.skipIf(not (hasattr(wexpect, 'legacy_wexpect')) or (hasattr(wexpect.spawn, 'interact')), "spawn does not support runtime interact switching.")
    def test_interact_dead(self):
        # Path of cmd executable:
        echo = 'echo hello'

        # Start the child process
        p = wexpect.spawn(echo)
        
        p.expect('hello')
        time.sleep(0.5)
        
        
        with self.assertRaises(wexpect.ExceptionPexpect):
            p.interact()

        with self.assertRaises(wexpect.ExceptionPexpect):
            p.stop_interact()
            
if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(InteractTestCase,'test')
