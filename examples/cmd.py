# A simple example code for wexpect

from __future__ import print_function

import sys
import os

here = os.path.dirname(os.path.abspath(__file__))
wexpectPath = os.path.dirname(here)
sys.path.insert(0, wexpectPath)

import wexpect

# Path of cmd executable:
cmdPathes = ['C:\Windows\System32\cmd.exe', 'cmd.exe', 'cmd']
cmdPrompt = '>'

for cmdPath in cmdPathes:
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

