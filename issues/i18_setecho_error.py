import wexpect
import time
import os

print(wexpect.__version__)

def test_setecho():
    # Path of cmd executable:
    cmdPath = 'cmd'
    cmdPrompt = '>'
    referenceOut = None
    
    # Start the child process
    p = wexpect.spawn(cmdPath)
    p.expect(cmdPrompt)
    
    p.setecho(0)                # SETECHO
    
    p.interact()
    for c in 'echo Hello':
        p.send(c)
        time.sleep(0.2)
    p.send(os.linesep)
    
    time.sleep(2)
    p.stop_interact()
    p.sendline('exit')
    
    
    # Start the child process
    p = wexpect.spawn(cmdPath)
    p.expect(cmdPrompt)
    
    p.setecho(1)                # SETECHO
    
    p.interact()
    for c in 'echo Hello':
        p.send(c)
        time.sleep(0.2)
    p.send(os.linesep)
    
    time.sleep(2)
    p.stop_interact()
    p.sendline('exit')
    
    
test_setecho()    
