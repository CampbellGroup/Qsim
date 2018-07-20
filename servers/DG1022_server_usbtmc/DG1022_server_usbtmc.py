"""
### BEGIN NODE INFO
[info]
name = DS1052E Scope Server
version = 1.0
description =
instancename = DS1052E Scope Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from twisted.internet.defer import returnValue
import os
from labrad.server import LabradServer, setting

dev_name = '/dev/ttyUSBRigolscope'


class DG1022_Rigol_Server(LabradServer):

	name = 'DG1022_Rigol_Server'

	def initServer(self):
		self.lookup = {'sine':'SIN', 'square':'SQU', 'ramp':'RAMP', 'pulse':'PULS', 'noise':'NOIS', 'DC' : 'DC', 'USER':'USER'}
		self.device = os.open(dev_name, os.O_RDWR)

	@setting(11, returns='s')
	def query_device(self, c):
		self.write("*IDN?")
		response = self.read()
		yield returnValue(response)

	@setting(12, channel='w', value = 'b')
	def set_output(self, c, channel, value):
		channel = self.parsechannel(channel)
		if value == True:
			yield self.write("OUTP" + str(channel) + " ON")
		elif value == False:
			yield self.write("OUTP" + str(channel) + " OFF")

	@setting(13, channel='w', function='s', frequency='v[Hz]', amplitude='v[V]', offset='v[V]')
	def applyWaveForm(self, c, function, frequency, amplitude, offset, channel=None):
		channel = self.parsechannel(channel)
		output = "APPL:" + self.lookup[function] + channel + ' ' + str(int(frequency['Hz'])) + ',' + str(
			amplitude['V']) + ',' + str(offset['V'])
		yield self.write(output)

	@setting(15, channel='w', function='s')
	def WaveFunction(self, c, channel, function=None):
		'''
		Changes wave form
		'''
		channel = self.parsechannel(channel)
		if function == None:
			output = "FUNC" + channel + "?"
			yield self.write(output)
			func = yield self.read()
			returnValue(func)
		else:
			output = "FUNC" + channel + " " + self.lookup[function]
			yield self.write(output)

	@setting(16, channel='w', frequency='v[Hz]')
	def Frequency(self, c, channel, frequency=None):
		'''
		Sets frequency
		'''
		channel = self.parsechannel(channel)
		if frequency == None:
			output = "FREQ" + channel + "?"
			yield self.write(output)
			freq = yield self.read()
			returnValue(freq)
		else:
			output = "FREQ " + channel + str(frequency['Hz'])
			yield self.write(output)

	@setting(17, channel='w', voltage='v[V]')
	def setDC(self, c, channel, voltage=None):
		'''
		sets DC output value
		'''
		channel = self.parsechannel(channel)
		if voltage == None:
			#            output = "VOLT:OFFS" + channel
			output = "APPL" + channel + "?"
			yield self.write(output)
			volts = yield self.read()
			volts = volts.split(',')
			volts = volts[3]
			volts = volts.strip('"')
			volts = float(volts)
			returnValue(volts)
		else:
			output = 'APPL:DC' + channel + ' DEF,DEF,' + str(voltage['V'])
			yield self.write(output)

	@setting(18, channel='w', offset='v[V]')
	def Offset(self, c, channel, offset=None):
		channel = self.parsechannel(channel)
		if offset == None:
			output = "VOLT:OFFS" + channel + "?"
			yield self.write(output)
			offset = yield self.read()
			returnValue(offset)
		else:
			output = "VOLT:OFFS" + channel + " " + str(offset['V'])
			yield self.write(output)

	@setting(19, channel='w', voltage='v[V]')
	def Amplitude(self, c, channel, voltage=None):
		'''
		sets amp
		'''
		channel = self.parsechannel(channel)
		if voltage == None:
			output = "VOLT" + channel + "?"
			yield self.write(output)
			volts = yield self.read()
			returnValue(volts)
		else:
			output = "VOLT" + channel + " " + str(voltage['V'])
			yield self.write(output)

	@setting(20, source='s')
	def AMSource(self, c, source):
		'''
		Select internal or external modulation source, the default is INT
		'''
		output = "AM:SOUR " + source
		yield self.write(output)

	@setting(21, function='s')
	def AMFunction(self, c, function):
		'''
		Select the internal modulating wave of AM
		In internal modulation mode, the modulating wave could be sine,
		square, ramp, negative ramp, triangle, noise or arbitrary wave, the
		default is sine.
		'''
		output = "AM:INT:FUNC " + self.lookup[function]
		yield self.write(output)

	@setting(22, frequency='v[Hz]')
	def AMFrequency(self, c, frequency):
		'''
		Set the frequency of AM internal modulation in Hz
		Frequency range: 2mHz to 20kHz
		'''
		output = "AM:INT:FREQ " + str(frequency['Hz'])
		yield self.write(output)

	@setting(23, depth='v')
	def AMDepth(self, c, depth):
		'''
		Set the depth of AM internal modulation in percent
		Depth range: 0% to 120%
		'''
		output = "AM:DEPT " + str(depth)
		yield self.write(output)

	@setting(24, state='b')
	def AMState(self, c, state):
		'''
		Disable or enable AM function
		'''
		if state:
			state = 'ON'
		else:
			state = 'OFF'

		output = "AM:STAT " + state
		yield self.write(output)

	@setting(25, source='s')
	def FMSource(self, c, source):
		'''
		Select internal or external modulation source, the default is INT
		'''
		output = "FM:SOUR " + source
		yield self.write(output)

	@setting(26, function='s')
	def FMFunction(self, c, function):
		'''
		In internal modulation mode, the modulating wave could be sine,
		square, ramp, negative ramp, triangle, noise or arbitrary wave, the
		default is sine
		'''
		output = "FM:INT:FUNC " + self.lookup[function]
		yield self.write(output)

	@setting(27, frequency='v[Hz]')
	def FMFrequency(self, c, frequency):
		'''
		Set the frequency of FM internal modulation in Hz
		Frequency range: 2mHz to 20kHz
		'''
		output = "FM:INT:FREQ " + str(frequency['Hz'])
		yield self.write(output)

	@setting(28, deviation='v')
	def FMDeviation(self, c, deviation):
		'''
		Set the frequency deviation of FM in Hz.
		'''
		output = "FM:DEV " + str(deviation)
		yield self.write(output)

	@setting(29, state='b')
	def FMState(self, c, state):
		'''
		Disable or enable FM function
		'''
		if state:
			state = 'ON'
		else:
			state = 'OFF'

		output = "FM:STAT " + state
		yield self.write(output)

	def write(self, data):
		os.write(self.device, data)

	def read(self):
		data = os.read(self.device, 300)
		return data


	def parsechannel(self, channel = None):
		if channel == 2:
			channel = ':CH2'
		else: channel = ''
		return channel

if __name__ == "__main__":
	from labrad import util
	util.runServer(DG1022_Rigol_Server())
