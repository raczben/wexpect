# A simple example code for wexpect written in python-2.7

from __future__ import print_function
import sys
import wexpect
import os

here = os.path.dirname(os.path.realpath(__file__))

# Path of python executable:
pythonInterp = sys.executable
prompt = ': '

# Start the child process
p = wexpect.spawn(pythonInterp, [here + '\\foo.py'])

# Wait for prompt
p.expect(prompt)
print(p.before)

# Send the 'small integer'
p.sendline('3')
p.expect(prompt)
print(p.before)

# print the texts
print(p.before, end='')
print(p.match.group(0), end='')

# Send the name
p.sendline('Bob')

# wait for program exit.
p.wait()

# print the texts
print(p.read(), end='')

