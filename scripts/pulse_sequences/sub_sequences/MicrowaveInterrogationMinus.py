from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class microwave_interogation_minus(pulse_sequence):

    required_parameters = [
                           ('MicrowaveInterogation', 'duration'),
                           ('MicrowaveInterogation', 'detuning'),
                           ('MicrowaveInterogation', 'power'),
                           ('Transitions', 'qubit_0'),
                           ('Transitions', 'qubit_plus'),
                           ('Transitions', 'qubit_minus'),
                           ('Pi_times', 'qubit_minus')
                           ]

    def sequence(self):
        p = self.parameters
        center = p.Transitions.qubit_minus
        DDS_freq = U(197.188, 'MHz') - (p.MicrowaveInterogation.detuning + center)
        duration = p.Pi_times.qubit_minus

        self.addDDS('Microwave_qubit',
                    self.start,
                    duration,
                    DDS_freq,
                    p.MicrowaveInterogation.power)

        self.end = self.start + p.MicrowaveInterogation.duration
