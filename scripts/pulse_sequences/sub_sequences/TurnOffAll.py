from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class turn_off_all(pulse_sequence):
	def sequence(self):
		dur = WithUnit(50.0, 'us')
		for channel in ['369DP','935SP',  'DopplerCoolingSP', 'StateDetectionSP', 'OpticalPumpingSP']:
			self.addDDS(channel, self.start, dur, WithUnit(0, 'MHz'), WithUnit(0, 'dBm'))
		self.end = self.start + dur