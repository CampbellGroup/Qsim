from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class test_sub_sequence(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Transitions', 'qubit_plus'),
        ('Transitions', 'qubit_minus'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'DP369_freq'),
    ]

    def sequence(self):
        p = self.parameters

        #  select which zeeman level to prepare
        """
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0

        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus

        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterogation.detuning + center)
        ttl_off = U(800.0, 'ns')
        ttl_delay = U(40.0, 'ns')
        start_delay = U(3.0, 'us')

        p['MicrowaveInterogation.duration'] = U(10.0, 'us')

        # pulse 1
        self.addTTL('MicrowaveTTL',
                    self.start + ttl_off + start_delay,
                    p.MicrowaveInterogation.duration/2.0 - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + ttl_off + start_delay,
                    p.MicrowaveInterogation.duration / 2.0)
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterogation.duration/2.0 + ttl_off + start_delay,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg'))

        # pulse 2
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

        # pulse 3
        self.addTTL('MicrowaveTTL',
                    self.start + 3.0 * p.MicrowaveInterogation.duration/2.0 + 3 * ttl_off + start_delay,
                    p.MicrowaveInterogation.duration/2.0 - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + 3.0 * p.MicrowaveInterogation.duration / 2.0 + 3 * ttl_off + start_delay,
                    p.MicrowaveInterogation.duration / 2.0 )
        self.addDDS('Microwave_qubit',
                    self.start + 3.0 * p.MicrowaveInterogation.duration/2.0 + 2 * ttl_off + start_delay ,
                    p.MicrowaveInterogation.duration/2.0 + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg'))

        self.addTTL('MicrowaveTTL2',
                    self.start,
                    2.0* p.MicrowaveInterogation.duration + 3*ttl_off + start_delay)

        self.end = self.start + 2.0 * p.MicrowaveInterogation.duration + 3.0* ttl_off + start_delay
        """
        self.addTTL('ReadoutCount',
                    self.start + U(1.0, 'ms'),
                    U(9.0, 'ms'))
        self.addTTL('DCShutter',
                    self.start,
                    U(10.0, 'ms'))

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    U(10.0, 'ms'),
                    p.ddsDefaults.doppler_cooling_freq,
                    p.ddsDefaults.doppler_cooling_power)

        self.addDDS('369DP',
                    self.start,
                    U(10.0, 'ms'),
                    p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq,
                    U(-4.0, 'dBm'))

        self.end = self.start + U(10.0, 'ms')