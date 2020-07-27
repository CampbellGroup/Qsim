from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence


class shelving(pulse_sequence):

    required_parameters = [
        ('Shelving', 'duration'),
        ('Shelving', 'assist_power'),
        ('Shelving', 'repump_power'),
        ('ddsDefaults', 'SP411_freq'),
        ('ddsDefaults', 'SP411_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_935_power')
    ]

    def sequence(self):
        p = self.parameters

        self.addDDS('411SP',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.SP411_freq,
                    p.ddsDefaults.SP411_power)

        self.addDDS('935SP',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.ddsDefaults.repump_935_power)

        self.end = self.start + p.Shelving.duration
