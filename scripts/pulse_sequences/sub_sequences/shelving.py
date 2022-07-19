from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence


class Shelving(pulse_sequence):

    required_parameters = [
        ('Shelving', 'duration'),
        ('Transitions', 'quadrupole'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'DP1_411_freq'),
        ('ddsDefaults', 'DP1_411_power'),
        ('ddsDefaults', 'DP2_411_freq'),
        ('ddsDefaults', 'DP2_411_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_935_power'),
        ('ddsDefaults', 'repump_976_freq'),
        ('ddsDefaults', 'repump_976_power'),
        ('ddsDefaults', 'DP369_freq'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('DopplerCooling', 'cooling_power'),
        ('DopplerCooling', 'repump_power'),
        ('DopplerCooling', 'detuning'),
        ('ddsDefaults', 'optical_pumping_freq'),
        ('ddsDefaults', 'optical_pumping_power'),
        ('ddsDefaults', 'metastable_qubit_dds_power'),
        ('ddsDefaults', 'metastable_qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        """
        This is the standard shelving stuff below
        """
        mode = p.Modes.shelving

        if mode == "Standard":
            self.addDDS('411DP1',
                        self.start,
                        p.Shelving.duration,
                        p.ddsDefaults.DP1_411_freq,
                        p.ddsDefaults.DP1_411_power)

            self.addDDS('935SP',
                        self.start,
                        p.Shelving.duration,
                        p.ddsDefaults.repump_935_freq,
                        p.ddsDefaults.repump_935_power)
            # This is (for the time being) NOT a 976, but the other 935 for 173.
            self.addDDS('976SP',
                        self.start,
                        p.Shelving.duration,
                        p.ddsDefaults.repump_976_freq,
                        p.ddsDefaults.repump_976_power)

            self.end = self.start + p.Shelving.duration

        if mode == "Cooling_on":
            self.addDDS('411DP1',
                        self.start,
                        p.Shelving.duration,
                        p.ddsDefaults.DP1_411_freq,
                        p.ddsDefaults.DP1_411_power)
            self.addDDS('369DP',
                        self.start,
                        p.Shelving.duration,
                        p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq + p.DopplerCooling.detuning / 2.0,
                        p.DopplerCooling.cooling_power)
            self.addDDS('935SP',
                        self.start,
                        p.Shelving.duration,
                        p.ddsDefaults.repump_935_freq,
                        p.DopplerCooling.repump_power)
            self.addDDS('976SP',
                        self.start,
                        p.Shelving.duration,
                        p.ddsDefaults.repump_976_freq,
                        p.ddsDefaults.repump_976_power)

            self.end = self.start + p.Shelving.duration