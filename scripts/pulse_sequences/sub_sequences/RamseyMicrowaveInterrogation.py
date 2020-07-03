from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class ramsey_microwave_interrogation(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('MicrowaveInterrogation', 'pulse_sequence'),
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

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterrogation.detuning + center)
        pulse_delay = U(800.0, 'us')

        if p.MicrowaveInterrogation.pulse_sequence != 'HPOnlyNoMixing':

            # first pi/2 pulse, DDS turns on 800 us before the ttl allows it through
            self.addTTL('MicrowaveTTL',
                        self.start + pulse_delay,
                        pi_time/2.0)

            self.addDDS('Microwave_qubit',
                        self.start,
                        pi_time/2.0 + pulse_delay,
                        DDS_freq,
                        p.MicrowaveInterrogation.power,
                        U(0.0, 'deg'))

            # second pi/2 pulse
            self.addTTL('MicrowaveTTL',
                        self.start + pulse_delay + pi_time/2.0 + p.EmptySequence.duration,
                        pi_time / 2.0)

            self.addDDS('Microwave_qubit',
                        self.start + pi_time/2.0 + pulse_delay,
                        pi_time/2.0 + p.EmptySequence.duration,
                        DDS_freq,
                        p.MicrowaveInterrogation.power,
                        p.MicrowaveInterrogation.microwave_phase)

        elif p.MicrowaveInterrogation.pulse_sequence == 'HPOnlyNoMixing':
            self.addTTL('MicrowaveTTL',
                        self.start,
                        pi_time/2.0)

            self.addTTL('MicrowaveTTL',
                        self.start + pi_time/2.0 + p.EmptySequence.duration,
                        pi_time/2.0)

        self.end = self.start + pi_time + p.EmptySequence.duration + pulse_delay
