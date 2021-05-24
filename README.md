# **wexpect**

[![Build status](https://ci.appveyor.com/api/projects/status/tbji72d5s0tagrt9?svg=true)](https://ci.appveyor.com/project/raczben/wexpect)
[![codecov](https://codecov.io/gh/raczben/wexpect/branch/master/graph/badge.svg)](https://codecov.io/gh/raczben/wexpect)
[![Documentation Status](https://readthedocs.org/projects/wexpect/badge/?version=latest)](https://wexpect.readthedocs.io/en/latest/?badge=latest)

*Wexpect* is a Windows variant of [pexpect](https://pexpect.readthedocs.io/en/stable/).

*Pexpect* is a Python module for spawning child applications and controlling
them automatically.

## You need wexpect if...

 - you want to control any windows console application from python script.
 - you want to write test-automation script for a windows console application.
 - you want to automate your job by controlling multiple application parallel, synchronously.

## **Install**

    pip install wexpect

## **Usage**

To interract with a child process use `spawn` method:

```python
import wexpect

prompt = '[A-Z]\:.+>'

child = wexpect.spawn('cmd.exe')
child.expect(prompt)    # Wait for startup prompt

child.sendline('dir')   # List the current directory
child.expect(prompt)

print(child.before)     # Print the list
child.sendline('exit')
```

For more information see [examples](./examples) folder.

---
## REFACTOR

**Refactor has been finished!!!** The default spawn class is `SpawnPipe` from now. For more
information read [history](https://wexpect.readthedocs.io/en/latest/history.html#refactor).

---
## What is wexpect?

Wexpect is a Python module for spawning child applications and controlling
them automatically. Wexpect can be used for automating interactive applications
such as ssh, ftp, passwd, telnet, etc. It can be used to a automate setup
scripts for duplicating software package installations on different servers. It
can be used for automated software testing. Wexpect is in the spirit of Don
Libes' Expect, but Wexpect is pure Python. Other Expect-like modules for Python
require TCL and Expect or require C extensions to be compiled. Wexpect does not
use C, Expect, or TCL extensions.

Original Pexpect should work on any platform that supports the standard Python pty module. While
Wexpect works on Windows platforms. The Wexpect interface focuses on ease of use so that simple
tasks are easy.

---
## Dev

Thanks for any contributing!

### Test

To run test, enter into the folder of the wexpect's repo then:

`python -m unittest`

### Deploy

The deployment itself is automated and done by [appveyor](https://ci.appveyor.com/project/raczben/wexpect).
See `after_test` section in [appveyor.yml](appveyor.yml) for more details.

The wexpect uses [pbr](https://docs.openstack.org/pbr/latest/) for managing releasing procedures.
The versioning is handled by the pbr. The *"master-version"* is the git tag. Pbr derives the package
version from the git tags.
