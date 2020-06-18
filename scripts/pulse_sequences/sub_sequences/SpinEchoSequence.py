from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
import numpy as np
from labrad.units import WithUnit as U


class spin_echo_sequence(pulse_sequence):
    """
    This is a BB1 corrective pulse sequence
    """

    required_parameters = [
        ('MicrowaveInterogation', 'duration'),
        ('MicrowaveInterogation', 'detuning'),
        ('MicrowaveInterogation', 'power'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Transitions', 'qubit_plus'),
        ('Transitions', 'qubit_minus'),
        ('Pi_times', 'qubit_0'),
        ('Pi_times', 'qubit_minus'),
        ('Pi_times', 'qubit_plus'),
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

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterogation.detuning + center)
        ttl_off = U(800.0, 'ns')
        ttl_delay = U(60.0, 'ns')
        start_delay = U(3.0, 'us')

        # Pi/2 around X
        self.addTTL('MicrowaveTTL',
                    self.start + ttl_off + start_delay,
                    p.MicrowaveInterogation.duration/2.0 - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + ttl_off + start_delay,
                    p.MicrowaveInterogation.duration / 2.0 )
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterogation.duration/2.0 + ttl_off + start_delay,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg'))

        # Pi around Y
        self.addTTL('MicrowaveTTL',
                    self.start + p.MicrowaveInterogation.duration/2.0 + 2 * ttl_off + start_delay,
                    p.MicrowaveInterogation.duration - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + p.MicrowaveInterogation.duration / 2.0 + 2 * ttl_off + start_delay,
                    p.MicrowaveInterogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + p.MicrowaveInterogation.duration/2.0 + ttl_off + start_delay,
                    p.MicrowaveInterogation.duration + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(90.0, 'deg'))

        # Pi/2 around X
        self.addTTL('MicrowaveTTL',
                    self.start + 3.0 * p.MicrowaveInterogation.duration/2.0 + 3 * ttl_off + start_delay,
                    p.MicrowaveInterogation.duration/2.0 - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + 3.0 * p.MicrowaveInterogation.duration / 2.0 + 3 * ttl_off + start_delay,
                    p.MicrowaveInterogation.duration / 2.0)
        self.addDDS('Microwave_qubit',
                    self.start + 3.0 * p.MicrowaveInterogation.duration/2.0 + 2 * ttl_off + start_delay,
                    p.MicrowaveInterogation.duration/2.0 + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg'))

        self.end = self.start + 2.0 * p.MicrowaveInterogation.duration + 3.0 * ttl_off + start_delay
