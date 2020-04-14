''' This script shows three method to terminate your application. `terminate_programmatically()`
shows the recommended way, which kills the child by sending the application specific exit command.
After that waiting for the terminaton is recommended.
`terminate_eof()` shows how to terminate child program by sending EOF character. Some program can be
terminated by sending EOF character. Waiting for the terminaton is recommended in this case too.
`terminate_terminate()` shows how to terminate child program by sending kill signal. Some
application requires sending SIGTERM to kill the child process. `terminate()` call `kill()`
function, which sends SIGTERM to child process. Waiting for the terminaton is not required
explicitly in this case. The wait is included in `terminate()` function.
'''

import wexpect

def terminate_programmatically():
    '''Terminate child program by command. This is the recommended method. Send your application's
    exit command to quit the child's process. After that wait for the terminaton.
    '''
    print('terminate_programmatically')

    # Start cmd as child process
    child = wexpect.spawn('cmd.exe')

    # Wait for prompt when cmd becomes ready.
    child.expect('>')

    # Exit from cmd
    child.sendline('exit')

    # Waiting for cmd termination.
    child.wait()

def terminate_eof():
    '''Terminate child program by sending EOF character. Some program can be terminated by sending
    an EOF character. Waiting for the terminaton is recommended in this case too.
    '''
    print('terminate_eof')

    # Start cmd as child process
    child = wexpect.spawn('cat')

    # Exit from cmd
    child.sendeof()

    # Waiting for cmd termination.
    child.wait()


def terminate_terminate():
    '''Terminate child program by sending kill signal. Some application requires sending SIGTERM to kill
    the child process. `terminate()` call `kill()` function, which sends SIGTERM to child process.
    Waiting for the terminaton is not required explicitly in this case. The wait is included in
    `terminate()` function.
    '''
    print('terminate_terminate')

    # Start cmd as child process
    child = wexpect.spawn('cmd.exe')

    # Wait for prompt when cmd becomes ready.
    child.expect('>')

    # Exit from cmd
    child.terminate()


terminate_programmatically()
terminate_eof()
terminate_terminate()
