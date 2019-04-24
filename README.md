# wexpect

wexpect is a Windows alternative of [pexpect](https://pexpect.readthedocs.io/en/stable/).

## pexpect

Pexpect is a Python module for spawning child applications and controlling
them automatically. Pexpect can be used for automating interactive applications
such as ssh, ftp, passwd, telnet, etc. It can be used to a automate setup
scripts for duplicating software package installations on different servers. It
can be used for automated software testing. Pexpect is in the spirit of Don
Libes' Expect, but Pexpect is pure Python. Other Expect-like modules for Python
require TCL and Expect or require C extensions to be compiled. Pexpect does not
use C, Expect, or TCL extensions. It should work on any platform that supports
the standard Python pty module. The Pexpect interface focuses on ease of use so
that simple tasks are easy.

There are two main interfaces to Pexpect -- the function, run() and the class,
spawn. You can call the run() function to execute a command and return the
output. This is a handy replacement for os.system().

For example::

    pexpect.run('ls -la')

The more powerful interface is the spawn class. You can use this to spawn an
external child command and then interact with the child by sending lines and
expecting responses.

For example::

    child = pexpect.spawn('scp foo myname@host.example.com:.')
    child.expect ('Password:')
    child.sendline (mypassword)

This works even for commands that ask for passwords or other input outside of
the normal stdio streams.

## Wexpect

Wexpect is a one-file code developed at University of Washington. There are several copy of this code,
with very few (almost none) documentation integration.

Here are some useful links:
 - https://gist.github.com/anthonyeden/8488763
 - https://mediarealm.com.au/articles/python-pexpect-windows-wexpect/

This repo tries to fix these limitations.

## Installation and limitation of wexpect

Current version does *not* work on python-3.x. You need to use **python 2.x** to use wexpect.

One (non stanbdard) package, **pypiwin32** needed to use wexpect.

    pip install pypiwin32
    
Dropping the wexpect.py file into your working directory is usually good enough instead of installing.
    
## Usage

See pexpect examples for usage.
