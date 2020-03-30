'''
This is is a very basic stdio handler script. This is used by python.py example.
'''

import time
import sys

# Read an integer from the user:

while True:
    print('Format:character,character_count,line_count,speed_ms> ', end='')
    command = input()
    (character,character_count,line_count,speed_ms) = command.split(',')
    character_count = int(character_count)
    speed_ms = int(speed_ms)
    line_count = int(line_count)

    if line_count<1:
        sys.exit(0)
    for _ in range(line_count):
        if speed_ms<0:
            print(character*character_count)
            sys.stdout.flush()
        else:
            for i in range(character_count):
                if i == character_count-1:
                    print(character)
                    sys.stdout.flush()
                else:
                    print(character, end='')
                    sys.stdout.flush()
                time.sleep(speed_ms/1000)
