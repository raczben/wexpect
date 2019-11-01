import wexpect
import time
import sys
import os

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)

from long_printer import puskas_wiki

print(wexpect.__version__)


# With quotes (C:\Program Files\Python37\python.exe needs quotes)
python_executable = '"' + sys.executable + '" '
child_script = here + '\\long_printer.py'


def main():
    longPrinter = python_executable + ' '  + child_script
    prompt = 'puskas> '
    
    # Start the child process
    p = wexpect.spawn(longPrinter)
    # Wait for prompt
    p.expect(prompt)
    
    try:
        for i in range(10):
            print('.', end='')
            p.sendline('0')
            p.expect(prompt)
            if p.before.splitlines()[1] != puskas_wiki[0]:
                print(p.before.splitlines()[1])
                raise Exception()
                
            p.sendline('all')
            p.expect(prompt)
            for a,b in zip(p.before.splitlines()[1:], puskas_wiki):
                if a!=b:
                    print(a)
                    print(b)
                    raise Exception()
                    
            for j, paragraph in enumerate(puskas_wiki):
                p.sendline(str(j))
                p.expect(prompt)
                if p.before.splitlines()[1] != paragraph:
                    print(p.before.splitlines()[1])
                    print(i)
                    print(j)
                    print(paragraph)
                    raise Exception()
    except:
        p.interact()
        time.sleep(5)
    else:
        print('')
        print('[PASS]')
        
            
main()
        
