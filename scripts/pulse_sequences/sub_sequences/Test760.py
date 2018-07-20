from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class test760(pulse_sequence):

    required_parameters = [
                           ('Shelving', 'duration')
                           ]

    def sequence(self):
        p = self.parameters
        self.end = self.start + p.Shelving.duration

        self.addDDS('RF_Drive',
                    self.start,
                    p.Shelving.duration/2.0,
                    U(110.0, 'MHz'),
                    U(-20.0, 'dBm'))

        self.addDDS('935SP',
                    self.start + p.Shelving.duration/2.0,
                    p.Shelving.duration/2.0,
                    U(200.0, 'MHz'),
                    U(-10.0, 'dBm'))

