from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class microwave_sequence_standard(pulse_sequence):

    required_parameters = [
                           ('MicrowaveInterogation', 'duration'),
                           ('MicrowaveInterogation', 'detuning'),
                           ('MicrowaveInterogation', 'power'),
                           ('Line_Selection', 'qubit'),
                           ('Transitions', 'qubit_0'),
                           ('Transitions', 'qubit_plus'),
                           ('Transitions', 'qubit_minus')
                           ]

    def sequence(self):
        p = self.parameters

        #  select which zeeman level to prepare
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0

        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus

        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus

        DDS_freq = U(377.1883927, 'MHz') - (p.MicrowaveInterogation.detuning + center)

        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterogation.duration,
                    DDS_freq,
                    p.MicrowaveInterogation.power)
        self.end = self.start + p.MicrowaveInterogation.duration
