# **wexpect examples**

There are several example usage of wexpect. Choose one as template of your application.

## hello_wexpect

[hello_wexpect](./hello_wexpect.py) is the simplest example. It starts a windows command interpreter
(aka. cmd) lists the current directory and exits.

## python

[python](./python.py) is a full custom example code. This example script runs [foo](./foo.py) python
program, and communicates with it. For better understanding please run natively foo<i></i>.py first, which
is a very basic stdio handler script.

## cmd_wrapper

[cmd_wrapper](./cmd_wrapper.py) is a simple wrapper around the cmd windows command interpreter. It
waits for commands executes them in the spawned cmd, and prints the results.
