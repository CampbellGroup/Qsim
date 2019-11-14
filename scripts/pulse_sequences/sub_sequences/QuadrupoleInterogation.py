from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class quadrupole_interogation(pulse_sequence):

    required_parameters = [
                           ('QuadrupoleInterogation', 'duration'),
                           ('QuadrupoleInterogation', 'detuning'),
                           ('QuadrupoleInterogation', 'power'),
                           ('Transitions', 'quadrupole'),
                           ]

    def sequence(self):
        p = self.parameters
        center = p.Transitions.quadrupole
        DDS_freq = U(250.0, 'MHz') + (p.QuadrupoleInterogation.detuning + center)/2.0
        self.addDDS('411DP',
                    self.start,
                    p.QuadrupoleInterogation.duration,
                    DDS_freq,
                    p.QuadrupoleInterogation.power)

        self.end = self.start + p.QuadrupoleInterogation.duration
