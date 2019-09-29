
import wexpect
import time
import sys
import os

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)

import i11_greek_printer

print(wexpect.__version__)

# With quotes (C:\Program Files\Python37\python.exe needs quotes)
python_executable = '"' + sys.executable + '" '
child_script = here + '\\i11_greek_printer.py'


def main():
    unicodePrinter = python_executable + ' '  + child_script
    prompt = 'give the name of a greek letter> '

    # Start the child process
    print('starting child: ' + unicodePrinter)
    p = wexpect.spawn(unicodePrinter)
    print('waiting for prompt')

    # Wait for prompt
    p.expect(prompt)
    print('Child prompt arrived, lets start commands!')

    # Send commands
    for letterName in i11_greek_printer.greekLetters.keys():
        p.sendline(letterName)
        p.expect(prompt)
        print(p.before.splitlines()[1])
        if i11_greek_printer.greekLetters[letterName] != p.before.splitlines()[1]:
            p.interact()
            time.sleep(5)
            raise Exception()
                 
        
main()
        
