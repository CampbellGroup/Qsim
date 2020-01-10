from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class metastable_microwave_interogation(pulse_sequence):

    required_parameters = [
                           ('MetastableMicrowaveInterogation', 'duration'),
                           ('MetastableMicrowaveInterogation', 'detuning'),
                           ('MetastableMicrowaveInterogation', 'power'),
                           ('Transitions', 'MetastableQubit'),
                           ]

    def sequence(self):
        p = self.parameters
        center = p.Transitions.MetastableQubit
        DDS_freq = U(300.000, 'MHz') + (p.MetastableMicrowaveInterogation.detuning + center)

        self.addDDS('3GHz_qubit',
                    self.start,
                    p.MetastableMicrowaveInterogation.duration,
                    DDS_freq,
                    p.MetastableMicrowaveInterogation.power)

        self.end = self.start + p.MetastableMicrowaveInterogation.duration
