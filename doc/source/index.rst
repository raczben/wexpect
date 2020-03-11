Wexpect version |version|
=========================

.. image:: https://ci.appveyor.com/api/projects/status/tbji72d5s0tagrt9?svg=true
   :target: https://ci.appveyor.com/project/raczben/wexpect
   :align: right
   :alt: Build status
   
.. warning::
    **UNDER CONSTRUCTION!!!**
    Documentation is in a very preliminary state. I'm learning sphinx and
    readthedocs.

*Wexpect* is a Windows variant of `Pexpect <https://pexpect.readthedocs.io/en/stable/>`_
Wexpect and Pexpect makes Python a better tool for controlling other applications.

Wexpect is a Python module for spawning child applications;
controlling them; and responding to expected patterns in their output.
Wexpect works like Don Libes' Expect. Wexpect allows your script to
spawn a child application and control it as if a human were typing
commands.

Wexpect can be used for automating interactive applications such as
ssh, ftp, passwd, telnet, etc. It can be used to a automate setup
scripts for duplicating software package installations on different
servers. It can be used for automated software testing.
Wexpect highly depends on Mark Hammond's `pywin32 <https://github.com/mhammond/pywin32>`_
which provides access to many of the Windows APIs from Python.

Install
^^^^^^^

Wexpect is on PyPI, and can be installed with standard tools::

    pip install wexpect

Hello Wexpect
^^^^^^^^^^^^^

To interract with a child process use :code:`spawn` method:

.. code-block:: python

  import wexpect 
  child = wexpect.spawn('cmd.exe')
  child.expect('>')
  child.sendline('ls')
  child.expect('>')
  print(child.before)
  child.sendline('exit')


For more information see [examples](./examples) folder.


Contents:
 

.. toctree::
   :maxdepth: 2

   api/index
   history

Wexpect is developed `on Github <http://github.com/raczben/wexpect>`_. Please
report `issues <https://github.com/raczben/wexpect/issues>`_ there as well.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
