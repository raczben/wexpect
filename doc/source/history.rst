History
=======

Wexpect was a one-file code developed at University of Washington. There were several
`copy <https://gist.github.com/anthonyeden/8488763>`_ and
`reference <https://mediarealm.com.au/articles/python-pexpect-windows-wexpect/>`_
to this code with very few (almost none) documentation nor integration.

This project fixes these limitations, with example codes, tests, and pypi integration.

Refactor
^^^^^^^^

The original wexpect was a monolith, one-file code, with several structural weaknesses. This leads
me to rewrite the whole code. The first variant of the new structure is delivered with
`v3.2.0 <https://pypi.org/project/wexpect/3.2.0/>`_. (The default is the old variant
(:code:`legacy_wexpect`) in v3.2.0. :code:`WEXPECT_SPAWN_CLASS` environment variable can choose the
new-structured implementation.) Now :code:`SpawnPipe` is the default spawn class.

Old vs new
^^^^^^^^^^

But what is the difference between the old and new and what was the problem with the old?

Generally, wexpect (both old and new) has three processes:

 - *host* is our original python script/program, which want to launch the child.
 - *console* is a process which started by the host, and launches the child. (This is a python script)
 - *child* is the process which want to be launched.

The child and the console has a common Windows console, distict from the host.

The :code:`legacy_wexpect`'s console is a thin script, almost do nothing. It initializes the Windows's
console, and monitors the host and child processes. The magic is done by the host process, which has
the :code:`switchTo()` and :code:`switchBack()` functions, which (de-) attaches the *child-console*
Windows-console. The host manipulates the child's console directly. This direct manipulation is the
main structural weakness. The following task/use-cases are hard/impossible:

  - thread-safe multiprocessing of the host.
  - logging (both console and host)
  - using in graphical IDE or with pytest
  - This variant is highly depends on the pywin32 package.

The new structure's console is a thick script. The console process do the major console manipulation,
which is controlled by the host via socket (see SpawnSocket) or named-pipe (SpawnPipe). The host
only process the except-loops.
