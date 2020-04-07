API documentation
=================

Wexpect symbols
---------------

Wexpect package has the following symbols. (Exported by :code:`__all__` in code:`__init__.py`)

.. _wexpect.spawn:

**spawn**

This is the main class interface for Wexpect. Use this class to start and control child applications.
There are two implementation: :class:`wexpect.host.SpawnPipe` uses Windows-Pipe for communicate child.
:class:`wexpect.SpawnSocket` uses TCP socket. Choose the default implementation with
:code:`WEXPECT_SPAWN_CLASS` environment variable, or the :class:`wexpect.host.SpawnPipe` will be
chosen by default.

.. _wexpect.SpawnPipe:

**SpawnPipe**

:class:`wexpect.host.SpawnPipe` is the default spawn class, but you can access it directly with its
exact name.

.. _wexpect.SpawnSocket:

**SpawnSocket**

:class:`wexpect.host.SpawnSocket` is the secondary spawn class, you can access it directly with its
exact name or by setting the :code:`WEXPECT_SPAWN_CLASS` environment variable to :code:`SpawnSocket`

.. _wexpect.run:

**run**

:meth:`wexpect.host.run` runs the given command; waits for it to finish; then returns all output as a string.
This function is similar to :code:`os.system()`.

.. _wexpect.EOF:

**EOF**

:class:`wexpect.wexpect_util.EOF` is an exception. This usually means the child has exited.

.. _wexpect.TIMEOUT:

**TIMEOUT**

:class:`wexpect.wexpect_util.TIMEOUT` raised when a read time exceeds the timeout.

.. _wexpect.__version__:

**__version__**

This gives back the version of the wexpect release. Versioning is handled by the
`pbr <https://pypi.org/project/pbr/>`_ package, which derives it from Git tags.

.. _wexpect.spawn_class_name:

**spawn_class_name**

Contains the default spawn class' name even if the user has not specified it. The value can be
:code:`SpawnPipe` or :code:`SpawnSocket`

.. _wexpect.ConsoleReaderSocket:

**ConsoleReaderSocket**

For advanced users only!
:class:`wexpect.console_reader.ConsoleReaderSocket`

.. _wexpect.ConsoleReaderPipe:

**ConsoleReaderPipe**

For advanced users only!
:class:`wexpect.console_reader.ConsoleReaderPipe`

Wexpect modules
---------------

.. toctree::
   :maxdepth: 2

   host
   wexpect_util
   console_reader
