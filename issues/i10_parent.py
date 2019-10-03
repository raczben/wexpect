import wexpect
import time
import sys
import os

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)

import i11_unicode_printer

print(wexpect.__version__)


# With quotes (C:\Program Files\Python37\python.exe needs quotes)
python_executable = '"' + sys.executable + '" '
child_script = here + '\\long_printer.py'


def main():
    longPrinter = python_executable + ' '  + child_script
    prompt = '> '
    
    # Start the child process
    p = wexpect.spawn(longPrinter)
    
    print('After Spawn')

    # Wait for prompt
    p.expect(prompt)
    print('After prompt')
    p.sendline('0')
    p.expect(prompt)
    print(p.before)
    p.sendline('all')
    print('After all')
    p.expect(prompt)
    print('After prompt')
    print(p.before)
    p.sendline('0')
    p.expect(prompt)
    print(p.before)
    p.sendline('1')
    p.expect(prompt)
    print(p.before)
    p.sendline('2')
    p.expect(prompt)
    print(p.before)
    p.sendline('all')
    p.expect(prompt)
    print(p.before)

        
main()
        
