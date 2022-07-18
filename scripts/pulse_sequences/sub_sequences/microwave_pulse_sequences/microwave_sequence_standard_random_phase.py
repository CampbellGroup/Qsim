from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
import numpy as np

class microwave_sequence_standard_random_phase(pulse_sequence):
    # this is a general microwave square pulse sequence where the different qubit lines
    # can be selected

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Transitions', 'qubit_plus'),
        ('Transitions', 'qubit_minus'),
        ('ddsDefaults', 'qubit_dds_freq')
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

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterrogation.detuning + center)
        phase = 360.0*np.random.rand()
        pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay
        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterrogation.duration + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phase, 'deg'))
        print(phase)
        self.end = self.start + p.MicrowaveInterrogation.duration + pulse_delay
