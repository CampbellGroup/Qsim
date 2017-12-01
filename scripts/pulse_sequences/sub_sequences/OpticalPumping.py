from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class optical_pumping(pulse_sequence):

    required_parameters = [
                           ('OpticalPumping', 'duration'),
                           ('OpticalPumping', 'power'),
                           ('OpticalPumping', 'detuning'),
                           ('Transitions', 'main_cooling_369')
                           ]

    def sequence(self):
        p = self.parameters
        self.addDDS('StateDetectionSP',
                    self.start,
                    p.OpticalPumping.duration,
                    U(110.0, 'MHz'),
                    p.OpticalPumping.power)

        self.addDDS('369DP',
                    self.start,
                    p.OpticalPumping.duration,
                    p.Transitions.main_cooling_369 + p.OpticalPumping.detuning/2.0,
                    U(-5.0, 'dBm'))

        self.addDDS('935SP',
                    self.start,
                    p.OpticalPumping.duration,
                    U(320.0, 'MHz'),
                    U(-1.0, 'dBm'))

        self.end = self.start + p.OpticalPumping.duration
