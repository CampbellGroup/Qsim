import labrad
import time
cxn = labrad.connect(name = "tickle script")
cxn2 = labrad.connect('169.232.156.230', name = "tickle script")

pmt = cxn.arduinocounter
dv = cxn.data_vault
rg = cxn2.rigol_dg1022_server

span = [120000, 140000] #hz
amp = 5 #volts
resolution = 100 # hz
chan = 1
waveform = 'sine'
offset = 0.0
average = 4

xvalues = range(span[0],span[1],resolution)


dv.cd('Tickle Scan', True)
filename = dv.new('Tickle Scan',[('freq', 'num')], [('kilocounts/sec','','num')])
window_name = 'V'


dv.add_parameter('Window', window_name)
dv.add_parameter('plotLive', True)

rg.set_output(True)
for i, freq in enumerate(xvalues):
	rg.apply_wave_form(chan, waveform, freq, amp, offset)
	counts = 0
	for j in range(average):	
		counts = pmt.get_current_counts() + counts
		time.sleep(0.1)
	counts = counts/average
	dv.add(freq, counts)
rg.set_output(False)



