
import wexpect
import time
import sys
import os

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)

import i11_unicode_printer

print(wexpect.__version__)

encodings = ['cp1250', 'utf-8']


# With quotes (C:\Program Files\Python37\python.exe needs quotes)
python_executable = '"' + sys.executable + '" '
child_script = here + '\\i11_unicode_printer.py'


def main():
    unicodePrinter = python_executable + ' '  + child_script
    prompt = '> '
    
    for ec in encodings:
        # Start the child process
        p = wexpect.spawn(unicodePrinter)

        # Wait for prompt
        p.expect(prompt)
        print('Child prompt arrived, lets set encoding!')
        p.sendline(ec)
        p.expect(prompt)

        # Send commands
        for cc in range(34, 500):
            p.sendline(str(cc))
            p.expect(prompt)
            print(p.before.splitlines()[1])
            if chr(int(cc)).encode("utf-8").decode(ec) != p.before.splitlines()[1]:
                p.interact()
                time.sleep(5)
                raise Exception()
                 
        
main()
        
