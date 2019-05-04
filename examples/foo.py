from __future__ import print_function
import time

print('Give a small integer: ', end='')
num = input()

for i in range(int(num)):
    print('waiter ' + str(i))
    time.sleep(0.2)

print('Give your name: ', end='')
name = input()
print('Hello ' + str(name), end='')