Examples
========

`hello_wexpect.py <https://github.com/raczben/wexpect/blob/master/examples/hello_wexpect.py>`_

    This is the simplest example. It starts a windows command interpreter (aka. cmd) lists the current
    directory and exits.

    .. code-block:: python

        import wexpect

        # Start cmd as child process
        child = wexpect.spawn('cmd.exe')

        # Wait for prompt when cmd becomes ready.
        child.expect('>')

        # Prints the cmd's start message
        print(child.before, end='')
        print(child.after, end='')

        # run list directory command
        child.sendline('ls')

        # Waiting for prompt
        child.expect('>')

        # Prints content of the directory
        print(child.before, end='')
        print(child.after, end='')

        # Exit from cmd
        child.sendline('exit')

        # Waiting for cmd termination.
        child.wait()


`terminaton.py <https://github.com/raczben/wexpect/blob/master/examples/terminaton.py>`_

    This script shows three method to terminate your application. `terminate_programmatically()`
    shows the recommended way, which kills the child by sending the application specific exit command.
    After that waiting for the terminaton is recommended.
    `terminate_eof()` shows how to terminate child program by sending EOF character. Some program can be
    terminated by sending EOF character. Waiting for the terminaton is recommended in this case too.
    `terminate_terminate()` shows how to terminate child program by sending kill signal. Some
    application requires sending SIGTERM to kill the child process. `terminate()` call `kill()`
    function, which sends SIGTERM to child process. Waiting for the terminaton is not required
    explicitly in this case. The wait is included in `terminate()` function.

    .. code-block:: python

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

            # Start cat as child process
            child = wexpect.spawn('cat')

            # Exit by sending EOF
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
