from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class TestSubSequence(pulse_sequence):
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
        ('Modes', 'laser_369'),
    ]

    def sequence(self):
        p = self.parameters

        duration = U(500, 'us')

        # self.addTTL('ReadoutCount',
        #              self.start,
        #              U(500, 'us'))
        #  # self.addTTL('DCShutter',
        #  #             self.start,
        #  #             U(10.0, 'ms'))
        #
        #  # self.addDDS('DopplerCoolingSP',
        #  #             self.start,
        #  #             U(10.0, 'ms'),
        #  #             p.ddsDefaults.doppler_cooling_freq,
        #  #             p.ddsDefaults.doppler_cooling_power)
        #
        #  self.addDDS('369DP',
        #              self.start,
        #              U(10.0, 'ms'),
        #              p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq,
        #              U(-4.0, 'dBm'))
        #
        #  self.end = self.start + U(10.0, 'ms')
        mode = p.Modes.laser_369

        if mode == 'Standard':
            self.addTTL('ReadoutCount',
                        self.start,
                        duration)
            self.addTTL('WindfreakSynthHDTTL',
                        self.start,
                        duration)
            self.end = self.start + duration
        elif mode == 'FiberEOM':
            self.addTTL('ReadoutCount',
                        self.start,
                        duration)
            self.addTTL('WindfreakSynthHDTTL',
                        self.start,
                        duration)
            self.end = self.start + duration
