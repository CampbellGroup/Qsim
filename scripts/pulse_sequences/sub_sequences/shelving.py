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
        self.addDDS('411DP1',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.DP1_411_freq,
                    p.ddsDefaults.DP1_411_power)

        #self.addTTL('411TTL',
        #            self.start,
        #            p.Shelving.duration)

        self.addDDS('935SP',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.ddsDefaults.repump_935_power)
        #This is (for the time being) NOT a 976, but the other 935 for 173.
        self.addDDS('976SP',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.repump_976_freq,
                    p.ddsDefaults.repump_976_power)
        # self.addDDS('3GHz_qubit',
        #            self.start,
        #            p.Shelving.duration,
        #            p.ddsDefaults.metastable_qubit_dds_freq,
        #            p.ddsDefaults.metastable_qubit_dds_power)
        self.end = self.start + p.Shelving.duration
