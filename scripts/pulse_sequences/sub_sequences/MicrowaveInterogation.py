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
        DDS_freq = U(200.0, 'MHz') + p.MicrowaveInterogation.detuning
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterogation.duration,
                    DDS_freq,
                    U(6.0, 'dBm'))
        self.end = self.start + p.MicrowaveInterogation.duration
