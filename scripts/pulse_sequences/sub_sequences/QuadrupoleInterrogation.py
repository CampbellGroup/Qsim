from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class quadrupole_interrogation(pulse_sequence):

    required_parameters = [
        ('QuadrupoleInterrogation', 'duration'),
        ('QuadrupoleInterrogation', 'detuning'),
        ('QuadrupoleInterrogation', 'power'),
        ('Transitions', 'quadrupole'),
        ('ddsDefaults', 'DP1_411_freq')
    ]

    def sequence(self):
        p = self.parameters

        center = p.Transitions.quadrupole
        DDS_freq = p.ddsDefaults.DP1_411_freq + (p.QuadrupoleInterrogation.detuning + center)/2.0

        self.addDDS('411DP1',
                    self.start,
                    p.QuadrupoleInterrogation.duration,
                    DDS_freq,
                    p.QuadrupoleInterrogation.power)

        self.end = self.start + p.QuadrupoleInterrogation.duration
