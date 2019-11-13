import wexpect
import time

def switch_back_error ():
    p2 = wexpect.spawn('echo blabla')
    
    # This is an essential wait:
    time.sleep(1)
    p2.expect(wexpect.EOF)
    
    
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
    
    p.interact()
    time.sleep(2)
        
    if 'hello' != p.before.splitlines()[1]:
        raise Exception("'hello' != p.before.splitlines()[1]")

if __name__ == '__main__':
    switch_back_error()

