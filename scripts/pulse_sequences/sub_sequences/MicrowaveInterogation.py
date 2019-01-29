from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class microwave_interogation(pulse_sequence):

    required_parameters = [
                           ('MicrowaveInterogation', 'duration'),
                           ('MicrowaveInterogation', 'detuning'),
                           ('Line_Selection', 'qubit'),
                           ('Transitions', 'qubit_0'),
                           ('Transitions', 'qubit_plus'),
                           ('Transitions', 'qubit_minus')
                           ]

    def sequence(self):
        p = self.parameters
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0

        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus

        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus

        DDS_freq = U(197.188, 'MHz') - (p.MicrowaveInterogation.detuning + center)
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterogation.duration,
                    DDS_freq,
                    U(6.0, 'dBm'))
        self.end = self.start + p.MicrowaveInterogation.duration
