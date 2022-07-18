from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class knill_pulse_area_correcting_sequence(pulse_sequence):
    """
     This sequence is based on the work by David Su, a modification of the Knill sequence that sacrifices
     correcting detuning errors for correcting amplitude errors.
     """

    required_parameters = [
                           ('MicrowaveInterrogation', 'duration'),
                           ('MicrowaveInterrogation', 'detuning'),
                           ('MicrowaveInterrogation', 'power'),
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

        ttl_off = U(800.0, 'ns')
        ttl_delay = U(60.0, 'ns')
        start_delay = U(3.0, 'us')

        # pulse 1
        self.addTTL('MicrowaveTTL',
                    self.start + ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterrogation.duration + ttl_off + start_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        # pulse 2
        self.addTTL('MicrowaveTTL',
                    self.start + p.MicrowaveInterrogation.duration + 2 * ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + p.MicrowaveInterrogation.duration + 2 * ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + p.MicrowaveInterrogation.duration + ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(180.0, 'deg'))

        # pulse 3
        self.addTTL('MicrowaveTTL',
                    self.start + 2 * p.MicrowaveInterrogation.duration + 3 * ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + 2 * p.MicrowaveInterrogation.duration + 3 * ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + 2 * p.MicrowaveInterrogation.duration + 2 * ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # pulse 4
        self.addTTL('MicrowaveTTL',
                    self.start + + 3 * p.MicrowaveInterrogation.duration + 4 * ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + + 3 * p.MicrowaveInterrogation.duration + 4 * ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + 3 * p.MicrowaveInterrogation.duration + 3 * ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(180.0, 'deg'))

        # pulse 5
        self.addTTL('MicrowaveTTL',
                    self.start + + 4 * p.MicrowaveInterrogation.duration + 5 * ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + + 4 * p.MicrowaveInterrogation.duration + 5 * ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + 4 * p.MicrowaveInterrogation.duration + 4 * ttl_off + start_delay,
                    p.MicrowaveInterrogation.duration + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        self.end = self.start + 5 * p.MicrowaveInterrogation.duration + 5 * ttl_off + start_delay
