import wexpect.host
import wexpect.legacy_wexpect

cmd = 'echo hello app'

p=wexpect.host.SpawnPipe(cmd)
p.expect('app')
print(p.before)

p=wexpect.legacy_wexpect.spawn(cmd)
p.expect('app')
print(p.before)

