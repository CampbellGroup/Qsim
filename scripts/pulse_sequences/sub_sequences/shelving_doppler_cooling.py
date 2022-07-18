from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence


class ShelvingDopplerCooling(pulse_sequence):

    required_parameters = [
        ('DopplerCooling', 'cooling_power'),
        ('DopplerCooling', 'repump_power'),
        ('DopplerCooling', 'detuning'),
        ('Shelving_Doppler_Cooling', 'duration'),
        ('Shelving_Doppler_Cooling', 'doppler_counts_threshold'),
        ('Shelving_Doppler_Cooling', 'method'),
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

        if p.Shelving_Doppler_Cooling.method == 'Standard':
            self.addDDS('DopplerCoolingSP',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration,
                        p.ddsDefaults.doppler_cooling_freq,
                        p.ddsDefaults.doppler_cooling_power)
            self.addDDS('369DP',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration,
                        p.Transitions.main_cooling_369/2.0 + p.ddsDefaults.DP369_freq + p.DopplerCooling.detuning/2.0,
                        p.DopplerCooling.cooling_power)
            self.addDDS('935SP',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration,
                        p.ddsDefaults.repump_935_freq,
                        p.DopplerCooling.repump_power)
            self.addDDS('760SP',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration,
                        p.ddsDefaults.repump_760_1_freq,
                        p.ddsDefaults.repump_760_1_power)
            self.addDDS('760SP2',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration,
                        p.ddsDefaults.repump_760_2_freq,
                        p.ddsDefaults.repump_760_2_power)
            # self.addDDS('ProtectionBeam',
            #             self.start,
            #             p.Shelving_Doppler_Cooling.duration,
            #             p.ddsDefaults.protection_beam_freq,
            #             p.ddsDefaults.protection_beam_power)
            self.addTTL('ReadoutCount',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration)
            self.addTTL('TimeResolvedCount',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration)
            self.end = self.start + p.Shelving_Doppler_Cooling.duration

        if p.Shelving_Doppler_Cooling.method == 'StandardFiberEOM':
            self.addDDS('369DP',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration,
                        p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq + p.DopplerCooling.detuning / 2.0,
                        p.DopplerCooling.cooling_power)
            self.addDDS('935SP',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration,
                        p.ddsDefaults.repump_935_freq,
                        p.DopplerCooling.repump_power)
            self.addDDS('976SP',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration,
                        p.ddsDefaults.repump_976_freq,
                        p.ddsDefaults.repump_976_power)
            self.addDDS('760SP',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration,
                        p.ddsDefaults.repump_760_1_freq,
                        p.ddsDefaults.repump_760_1_power)
            self.addDDS('760SP2',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration,
                        p.ddsDefaults.repump_760_2_freq,
                        p.ddsDefaults.repump_760_2_power)
            self.addTTL('ReadoutCount',
                        self.start,
                        p.Shelving_Doppler_Cooling.duration)
            self.end = self.start + p.Shelving_Doppler_Cooling.duration
