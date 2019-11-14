import wexpect
import time

p = wexpect.spawn('uname')
time.sleep(0.5)
p.expect(wexpect.EOF)
print(p.before)

p = wexpect.spawn('uname')
time.sleep(0.8)
p.expect(wexpect.EOF)
print(p.before)

p = wexpect.spawn('uname')
time.sleep(1.1)
p.expect(wexpect.EOF)
print(p.before)

p = wexpect.spawn('uname')
time.sleep(1.5)
p.expect(wexpect.EOF)
print(p.before)