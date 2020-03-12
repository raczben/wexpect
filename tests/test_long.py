import wexpect
import unittest
import sys
import os
from tests import PexpectTestCase
from . import long_printer

puskas_wiki = long_printer.puskas_wiki

class TestCaseLong(PexpectTestCase.PexpectTestCase):
    def test_long (self):
    
        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, here)

        # With quotes (C:\Program Files\Python37\python.exe needs quotes)
        python_executable = '"' + sys.executable + '" '
        child_script = here + '\\long_printer.py'


        longPrinter = python_executable + ' '  + child_script
        prompt = 'puskas> '
        
        # Start the child process
        p = wexpect.spawn(longPrinter)
        # Wait for prompt
        p.expect(prompt)
        
        for i in range(10):
            p.sendline('0')
            p.expect(prompt)
            self.assertEqual(p.before.splitlines()[1], puskas_wiki[0])
                
            p.sendline('all')
            p.expect(prompt)
            for a,b in zip(p.before.splitlines()[1:], puskas_wiki):
                self.assertEqual(a, b)
                    
            for j, paragraph in enumerate(puskas_wiki):
                p.sendline(str(j))
                p.expect(prompt)
                self.assertEqual(p.before.splitlines()[1], paragraph)
            

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(TestCaseLong,'test')


        
