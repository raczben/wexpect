import wexpect
import time

print(wexpect.__version__)


def testPath():
    # Path of cmd executable:
    cmdPath = 'cmd'
    cmdPrompt = '>'
    referenceOut = None

    while True:
        # Start the child process
        p = wexpect.spawn(cmdPath)

        # Wait for prompt
        p.expect(cmdPrompt)

        # Send a command
        p.sendline('ls')
        # time.sleep(0.6) <= this sleep solve...
        p.expect(cmdPrompt)
        
        print(cmdPath + " >>" + p.before + '<<')
        if referenceOut:
            if referenceOut != p.before:
                p.interact()
                time.sleep(5)
                raise Exception()
        else:
            referenceOut = p.before
        
testPath()
