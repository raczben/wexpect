import wexpect.host
import wexpect.legacy_wexpect
import time

cmd = 'echo hello app'

p=wexpect.host.SpawnPipe(cmd)
p.expect('app')
print(p.before)
del(p)

time.sleep(3)

p=wexpect.legacy_wexpect.spawn(cmd)
time.sleep(.5)
p.expect('app')
print(p.before)
time.sleep(5)

