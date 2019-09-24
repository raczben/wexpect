'''
This is is a very basic stdio handler script. This is used by python.py example.
'''

import time


print('Welcome!')

while True:
    print('>', end='')
    cmd = input()

    # Wait the given time
    if cmd == 'ls':
        print('apple\tbanana\tmelone\tcherry')
        print('pepper tomato\tcorn cabbage')
        print('apple banana\tmelone\tcherry2')
        print('pepper tomato\tcorn cabbage2')
        continue
    if cmd == 'exit':
        break
    else:
        print('unknown command')