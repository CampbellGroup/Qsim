from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class test_sub_sequence(pulse_sequence):

    required_parameters = [
                           ('TestSequence','duration'),
                           ]

    def sequence(self):

        p = self.parameters

        self.addTTL('DopplerCoolingShutter',
                    self.start - U(8.0, 'ms'),
                    p.TestSequence.duration)

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.TestSequence.duration,
                    U(110.0, 'MHz'),
                    U(-20.8, 'dBm'))

        self.addDDS('369DP',
                    self.start,
                    p.TestSequence.duration,
                    U(200.0, 'MHz'),
                    U(-0.1, 'dBm'))

        self.end = self.start + p.TestSequence.duration
        
