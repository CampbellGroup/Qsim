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
        qubit_freq = U(12.642812118, 'GHz') + p.MicrowaveInterogation.detuning
        DDS_freq = 30 - (qubit_freq['MHz']/3. - 10.*(int(qubit_freq['MHz']/30.)))
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterogation.duration,
                    U(DDS_freq, 'MHz'),
                    U(-11.0, 'dBm'))
        self.end = self.start + p.MicrowaveInterogation.duration
