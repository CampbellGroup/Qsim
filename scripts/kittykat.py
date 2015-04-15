import labrad
import time
cxn = labrad.connect(name = 'kittykat')
kk = cxn.arduinottl

def kittykat(delay):
	while True:
		kk.ttl_output(10, True)
		time.sleep(delay)
		kk.ttl_output(10, False)
		time.sleep(delay)

