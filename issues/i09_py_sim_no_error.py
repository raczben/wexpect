
import wexpect
import time

print(wexpect.__version__)


def testPath():
    # Path of cmd executable:
    cmdPath = 'python bugfix\\bla.py'
    cmdPrompt = '> '
    referenceOut = None

    while True:
        # Start the child process
        p = wexpect.spawn(cmdPath)

        # Wait for prompt
        p.expect(cmdPrompt)
        # Wait for prompt
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
        
