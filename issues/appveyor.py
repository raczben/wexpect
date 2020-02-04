import wexpect.host
import wexpect.legacy_wexpect
import time

cmd = 'echo hello app'

p=wexpect.host.SpawnPipe(cmd)

time.sleep(3)

p=wexpect.legacy_wexpect.spawn(cmd)
time.sleep(3)

