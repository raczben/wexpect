'''
This is is a very basic stdio handler script. This is used by python.py example.
'''

import time

# Read an integer from the user:
print('Give a small integer: ', end='')
num = input()

# Wait the given time
for i in range(int(num)):
    print('waiter ' + str(i))
    time.sleep(0.2)

# Ask the name of the user to say hello.
print('Give your name: ', end='')
name = input()
print('Hello ' + str(name), end='')
