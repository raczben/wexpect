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
 - you want to automate your job by controlling multiple application parallel, synchoronusly.

## **Install**

    pip install wexpect

## **Usage**

To interract with a child process use `spawn` method:

```python
import wexpect 
child = wexpect.spawn('cmd.exe')
child.expect('>')
child.sendline('ls')
child.expect('>')
print(child.before)
child.sendline('exit')
```

For more information see [examples](./examples) folder.

---
## **REFACTOR**

The original wexpect has some structural weakness, which leads me to rewrite the whole code. The
first variant of the new structure is delivered with [v3.2.0](https://pypi.org/project/wexpect/3.2.0/).
Note, that the default is the old variant (`legacy_wexpect`), to use the new you need to set the
`WEXPECT_SPAWN_CLASS` environment variable to `SpawnPipe` or `SpawnSocket`, which are the two new
structured spawn class.

### Old vs new

But what is the difference between the old and new and what was the problem with the old?

Generally, wexpect (both old and new) has three processes:
 
 - *host* is our original pyton script/program, which want to launch the child.
 - *console* is a process which started by the host, and launches the child. (This is a python script)
 - *child* is the process which want to be launced.
 
The child and the console has a common Windows console, distict from the host.

The `legacy_wexpect`'s console is a thin script, almost do nothing. It initializes the Windows's
console, and monitors the host and child processes. The magic is done by the host process, which has
the switchTo() and switchBack() functions, which (de-) attaches the *child-console* Windows-console.
The host manipulates the child's console directly. This direct manipuation is the structural weakness.
The following task/usecases are hard/impossibile:

  - thread-safe multiprocessing of the host.
  - logging (both console and host)
  - using in grapichal IDE or with pytest
  - This variant is highly depends on the pywin32 package.

The new structure's console is a thik script. The console process do the major console manipulation,
which is controlled by the host via socket (see SpawnSocket) or named-pipe (SpawnPipe). The host
only process the except-loops.

---
## What is it?

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


### History

Wexpect is a one-file code developed at University of Washington. There are several
[copy](https://gist.github.com/anthonyeden/8488763) and
[reference](https://mediarealm.com.au/articles/python-pexpect-windows-wexpect/)
to this code with very few (almost none) documentation nor integration.

This repo tries to fix these limitations, with a few example code and pypi integration.


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
 
## Basic behaviour

Let's go through the example code:

```python
import wexpect 
child = wexpect.spawn('cmd.exe')
child.expect('>')
child.sendline('ls')
child.expect('>')
print(child.before)
child.sendline('exit')
```

### spawn()

`child = wexpect.spawn('cmd.exe')`

Call trace:

 - ::spawn                          
 - spawn_windows::__init__() 
 - spawn_windows::_spawn()   
 - Wtty::spawn()              
 - Wtty::startChild()        
 - win32process.CreateProcess()  
 
 
### expect()

`child.expect('>')`

Call trace:

 - spawn_windows::expect()      
 - spawn_windows::expect_list() 
 - spawn_windows::expect_loop()  
 - spawn_windows::read_nonblocking()
 - Wtty::read_nonblocking()
 - Wtty::readConsoleToCursor()
 - Wtty::readConsole()           
 - __consout.ReadConsoleOutputCharacter()
    

### sendline()

`child.sendline('ls')`

 - spawn_windows::sendline()    
 - spawn_windows::send()      
 - Wtty::write()       
