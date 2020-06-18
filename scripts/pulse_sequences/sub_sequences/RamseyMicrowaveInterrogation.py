from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class ramsey_microwave_interrogation(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterogation', 'detuning'),
        ('MicrowaveInterogation', 'power'),
        ('MicrowaveInterogation', 'microwave_phase'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Transitions', 'qubit_plus'),
        ('Transitions', 'qubit_minus'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('EmptySequence', 'duration'),
        ('Pi_times', 'qubit_0'),
        ('Pi_times', 'qubit_minus'),
        ('Pi_times', 'qubit_plus'),
                           ]

    def sequence(self):
        p = self.parameters

        #  select which mcirwave transition to drive
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0
            pi_time = p.Pi_times.qubit_0

        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus
            pi_time = p.Pi_times.qubit_plus

        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus
            pi_time = p.Pi_times.qubit_minus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterogation.detuning + center)

        self.addTTL('MicrowaveTTL',
                    self.start,
                    pi_time + p.EmptySequence.duration)
        self.addTTL('MicrowaveTTL3',
                    self.start,
                    pi_time + p.EmptySequence.duration)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + pi_time/2.0 + p.EmptySequence.duration,
                    pi_time/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    p.MicrowaveInterogation.microwave_phase)

        self.end = self.start + pi_time + p.EmptySequence.duration
