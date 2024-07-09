from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence


class ShelvingDopplerCooling(PulseSequence):

    required_parameters = [
        ('DopplerCooling', 'cooling_power'),
        ('DopplerCooling', 'repump_power'),
        ('DopplerCooling', 'detuning'),
        ('Shelving_Doppler_Cooling', 'duration'),
        ('Shelving_Doppler_Cooling', 'doppler_counts_threshold'),
        ('Modes', 'laser_369'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_976_freq'),
        ('ddsDefaults', 'repump_976_power'),
        ('ddsDefaults', 'repump_760_1_freq'),
        ('ddsDefaults', 'repump_760_1_power'),
        ('ddsDefaults', 'repump_760_2_freq'),
        ('ddsDefaults', 'repump_760_2_power'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('ddsDefaults', 'DP369_freq'),
        ('ddsDefaults', 'protection_beam_freq'),
        ('ddsDefaults', 'protection_beam_power')
    ]

    def sequence(self):
        p = self.parameters

        mode = p.modes.laser_369

        if mode == 'Standard':
            self.add_dds('DopplerCoolingSP',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration,
                         p.ddsDefaults.doppler_cooling_freq,
                         p.ddsDefaults.doppler_cooling_power)
            self.add_dds('369DP',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration,
                         p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq + p.DopplerCooling.detuning / 2.0,
                         p.DopplerCooling.cooling_power)
            self.add_dds('935SP',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration,
                         p.ddsDefaults.repump_935_freq,
                         p.DopplerCooling.repump_power)
            self.add_dds('760SP',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration,
                         p.ddsDefaults.repump_760_1_freq,
                         p.ddsDefaults.repump_760_1_power)
            self.add_dds('760SP2',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration,
                         p.ddsDefaults.repump_760_2_freq,
                         p.ddsDefaults.repump_760_2_power)
            self.add_ttl('ReadoutCount',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration)
            self.add_ttl('TimeResolvedCount',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration)
            self.end = self.start + p.Shelving_Doppler_Cooling.duration

        if mode == 'FiberEOM' or mode == 'FiberEOM173':
            self.add_dds('369DP',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration,
                         p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq + p.DopplerCooling.detuning / 2.0,
                         p.DopplerCooling.cooling_power)
            self.add_dds('935SP',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration,
                         p.ddsDefaults.repump_935_freq,
                         p.DopplerCooling.repump_power)
            self.add_dds('976SP',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration,
                         p.ddsDefaults.repump_976_freq,
                         p.ddsDefaults.repump_976_power)
            self.add_dds('760SP',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration,
                         p.ddsDefaults.repump_760_1_freq,
                         p.ddsDefaults.repump_760_1_power)
            self.add_dds('760SP2',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration,
                         p.ddsDefaults.repump_760_2_freq,
                         p.ddsDefaults.repump_760_2_power)
            self.add_ttl('ReadoutCount',
                         self.start,
                         p.Shelving_Doppler_Cooling.duration)
            self.end = self.start + p.Shelving_Doppler_Cooling.duration
