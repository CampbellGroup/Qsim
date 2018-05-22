from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class test760(pulse_sequence):

    required_parameters = [
                           ('Shelving', 'duration')
                           ]

    def sequence(self):
        p = self.parameters
        self.end = self.start + p.Shelving.duration

        self.addDDS('ModeLockedSP',
                    self.start,
                    p.Shelving.duration,
                    U(320.0, 'MHz'),
                    U(-10.0, 'dBm'))
