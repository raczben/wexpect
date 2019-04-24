# A simple example code for wexpect written in python-2.7

from __future__ import print_function
import wexpect

# Path of cmd executable:
cmdPath = 'C:\Windows\System32\cmd.exe'
cmdPrompt = '>'

# Start the child process
p = wexpect.spawn(cmdPath)

# Wait for prompt
p.expect(cmdPrompt)

# print the texts
print(p.before, end='')
print(p.match.group(0), end='')

# Send a command
p.sendline('ls')
p.expect(cmdPrompt)

# print the texts
print(p.before, end='')
print(p.match.group(0), end='')

