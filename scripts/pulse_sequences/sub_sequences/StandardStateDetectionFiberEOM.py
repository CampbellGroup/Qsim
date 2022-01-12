from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class standard_state_detection_fiber_eom(pulse_sequence):

    required_parameters = [
        ('StandardStateDetection', 'duration'),
        ('StandardStateDetection', 'CW_power'),
        ('StandardStateDetection', 'repump_power'),
        ('StandardStateDetection', 'detuning'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'state_detection_freq'),
        ('ddsDefaults', 'state_detection_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('ddsDefaults', 'DP369_freq')
    ]

    def sequence(self):
        p = self.parameters

        self.addTTL('WindfreakSynthHDTTL',
                   self.start,
                   p.StandardStateDetection.duration)

        self.addTTL('ReadoutCount',
                    self.start,
                    p.StandardStateDetection.duration)

        self.addDDS('935SP',
                    self.start,
                    p.StandardStateDetection.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.StandardStateDetection.repump_power)

        self.addDDS('369DP',
                    self.start,
                    p.StandardStateDetection.duration,
                    p.Transitions.main_cooling_369/2.0 + p.ddsDefaults.DP369_freq + p.StandardStateDetection.detuning/2.0,
                    p.StandardStateDetection.CW_power)

        self.end = self.start + p.StandardStateDetection.duration
