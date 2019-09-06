# A simple example code for wexpect

from __future__ import print_function

import sys
import os
import re

here = os.path.dirname(os.path.abspath(__file__))
wexpectPath = os.path.dirname(here)

import wexpect

# Path of cmd executable:
cmd_exe = 'cmd'
# The prompt should be more sophisticated than just a '>'.
cmdPrompt = re.compile('[A-Z]\:.+>')

# Start the child process
p = wexpect.spawn(cmd_exe)

# Wait for prompt
p.expect(cmdPrompt, timeout = 5)

# print the texts
print(p.before, end='')
print(p.match.group(0), end='')


while True:

    # Wait and run a command.
    command = input()
    p.sendline(command)
    
    try:
        # Wait for prompt
        p.expect(cmdPrompt)
        
        # print the texts
        print(p.before, end='')
        print(p.match.group(0), end='')
    
    except wexpect.EOF:
        # The program has exited
        print('The program has exied... BY!')
        break
