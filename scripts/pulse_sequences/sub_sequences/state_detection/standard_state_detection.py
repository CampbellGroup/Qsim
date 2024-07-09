from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence


class StandardStateDetection(PulseSequence):

    required_parameters = [
        ('StandardStateDetection', 'duration'),
        ('StandardStateDetection', 'CW_power'),
        ('StandardStateDetection', 'repump_power'),
        ('StandardStateDetection', 'detuning'),
        ('StandardStateDetection', 'method'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'state_detection_freq'),
        ('ddsDefaults', 'state_detection_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('ddsDefaults', 'DP369_freq'),
        ('Modes', 'laser_369'),
    ]

    def sequence(self):
        p = self.parameters

        mode = p.Modes.laser_369

        if mode == 'Standard':
            self.add_ttl('ReadoutCount',
                         self.start,
                         p.StandardStateDetection.duration)
            self.add_dds('935SP',
                         self.start,
                         p.StandardStateDetection.duration,
                         p.ddsDefaults.repump_935_freq,
                         p.StandardStateDetection.repump_power)
            self.add_dds('StateDetectionSP',
                         self.start,
                         p.StandardStateDetection.duration,
                         p.ddsDefaults.state_detection_freq,
                         p.ddsDefaults.state_detection_power)
            self.add_dds('369DP',
                         self.start,
                         p.StandardStateDetection.duration,
                         p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq + p.StandardStateDetection.detuning / 2.0,
                         p.StandardStateDetection.CW_power)
            self.end = self.start + p.StandardStateDetection.duration

        elif mode == 'FiberEOM' or mode == 'FiberEOM173':
            self.add_ttl('ReadoutCount',
                         self.start,
                         p.StandardStateDetection.duration)
            self.add_ttl('WindfreakSynthHDTTL',
                         self.start,
                         p.StandardStateDetection.duration)
            self.add_dds('935SP',
                         self.start,
                         p.StandardStateDetection.duration,
                         p.ddsDefaults.repump_935_freq,
                         p.StandardStateDetection.repump_power)
            self.add_dds('369DP',
                         self.start,
                         p.StandardStateDetection.duration,
                         p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq + p.StandardStateDetection.detuning / 2.0,
                         p.StandardStateDetection.CW_power)
            self.end = self.start + p.StandardStateDetection.duration

        else:
            print('unknown laser_369 mode')
