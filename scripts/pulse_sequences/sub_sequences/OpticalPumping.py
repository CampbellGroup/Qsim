from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class optical_pumping(pulse_sequence):

    required_parameters = [
                           ('OpticalPumping', 'duration'),
                           ('OpticalPumping', 'power'),
                           ('OpticalPumping', 'detuning'),
                           ('OpticalPumping', 'repump_power'),
                           ('Transitions', 'main_cooling_369'),
                           ('DopplerCooling', 'detuning')
                           ]

    def sequence(self):
        p = self.parameters
        extra_935 = U(100.0, 'us')
        self.addDDS('OpticalPumpingSP',
                    self.start,
                    p.OpticalPumping.duration,
                    U(110.0 + 4.0, 'MHz'),
                    U(-15.9, 'dBm'))

        self.addDDS('369DP',
                    self.start,
                    p.OpticalPumping.duration,
                    p.Transitions.main_cooling_369/2 + U(200.0 - 4.0/2.0, 'MHz') + p.OpticalPumping.detuning/2.0,
                    p.OpticalPumping.power)

        self.addDDS('935SP',
                    self.start,
                    p.OpticalPumping.duration + extra_935,
                    U(320.0, 'MHz'),
                    p.OpticalPumping.repump_power)

        self.addDDS('760SP',
                    self.start,
                    p.OpticalPumping.duration,
                    U(320.0, 'MHz'),
                    U(-2.0,  'dBm'))

        self.end = self.start + p.OpticalPumping.duration + extra_935
