# **wexpect**

*Wexpect* is a Windows variant of [pexpect](https://pexpect.readthedocs.io/en/stable/).

*Pexpect* is a Python module for spawning child applications and controlling
them automatically.

**!! UPDATE !!**

I'm glad to announce that python-3 is supported form version 2.3.3

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
```

For more information see [examples](./examples) folder.

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
## Installation of wexpect

### Standard installation

This version is uploaded to pypi server so you can easily install with pip:

    pip install wexpect
    
### Manual installation

Because this is a tiny project dropping the wexpect.py file into your working directory is usually
good enough instead of installing. However in this case you need to install manually the one dependence.

One (non stanbdard) package, **pypiwin32** is needed by wexpect.

    pip install pypiwin32
    
    
---
## Dev

Thanks for any contributing!

### Test

To run test, enter into the folder of the wexpect's repo then:

`python -m unittest`

Note that `tests.test_constructor.TestCaseConstructor.test_constructor` test fails due to
[STDERR isn't handled properly #2](https://github.com/raczben/wexpect/issues/2).

### Release

The wexpect uses [pbr](https://docs.openstack.org/pbr/latest/) for managing releasing procedures.
*Pre-release tasks:*

 - First of all be sure that your modification is good, by running the tests.
 - Commit your modification.
 - Create a test build `python -m setup sdist`
 - Upload the test `twine upload -r testpypi dist\wexpect-<VERSION>.tar.gz`  (You must install twine first.)
 - create virtualenv `virtualenv wexpectPy`
 - Activate the virtualenv `.\Scripts\activate.bat`
 - Install the test build `python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple wexpect`
 - run `python -c "import wexpect;print(wexpect.__version__)"` 
 
*Release tasks:*

 - Tag your commit (see the version tag format.)
 - Run `python -m setup sdist`
 - Upload the archive using: `twine upload dist/wexpect-<VERSION>.tar.gz`
 - create virtualenv `virtualenv wexpectPy2`
 - Activate the virtualenv `.\Scripts\activate.bat`
 - Install the test build `python -m pip install wexpect`
 - run `python -c "import wexpect;print(wexpect.__version__)"` 
 
Test 
 This means that you should r
 




