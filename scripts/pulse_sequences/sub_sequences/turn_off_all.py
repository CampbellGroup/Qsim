from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class turn_off_all(pulse_sequence):

    def sequence(self):
        dur = WithUnit(50, 'us')
        for channel in ['369']:
            self.addDDS(channel, self.start, dur, WithUnit(0, 'MHz'), WithUnit(0, 'dBm'))
        self.end = self.start + dur
