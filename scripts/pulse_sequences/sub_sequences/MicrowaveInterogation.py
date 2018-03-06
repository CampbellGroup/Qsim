from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class microwave_interogation(pulse_sequence):

    required_parameters = [
                           ('MicrowaveInterogation', 'duration'),
                           ('MicrowaveInterogation', 'detuning'),
                           ('Transitions', 'qubit_0')
                           ]

    def sequence(self):
        p = self.parameters

        self.addDDS('PLL_Reference_RF',
                    self.start,
                    p.MicrowaveInterogation.duration,
                    (p.Transitions.qubit_0 + p.MicrowaveInterogation.detuning),
                    U(7.0, 'dBm'))
        self.end = self.start + p.MicrowaveInterogation.duration
