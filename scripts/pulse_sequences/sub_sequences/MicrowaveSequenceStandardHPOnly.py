from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class microwave_sequence_standard_hp_only(pulse_sequence):
    # this sequence is for when we use the DDS as a reference for the HP and
    # want to keep it on at all times, we will not change the oscillator frequency

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
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

        DDS_freq = p.ddsDefaults.qubit_dds_freq

        self.addTTL('MicrowaveTTL',
                    self.start,
                    p.MicrowaveInterrogation.duration)

        self.end = self.start + p.MicrowaveInterrogation.duration