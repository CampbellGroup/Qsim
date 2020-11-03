from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class double_pass_369(pulse_sequence):

    required_parameters = [
        ('DoublePass369', 'duration'),
        ('DoublePass369', 'power'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'DP369_freq')
    ]

    def sequence(self):
        p = self.parameters

        self.addDDS('369DP',
                    self.start,
                    p.DoublePass369.duration,
                    p.Transitions.main_cooling_369/2.0 + p.ddsDefaults.DP369_freq,
                    p.DoublePass369.power)

        self.end = self.start + p.DoublePass369.duration
