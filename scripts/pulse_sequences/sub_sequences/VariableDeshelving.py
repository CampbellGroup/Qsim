from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class variable_deshelving(pulse_sequence):

    required_parameters = [
        ('VariableDeshelving', 'duration'),
        ('Deshelving', 'power1'),
        ('Deshelving', 'power2'),
        ('DopplerCooling', 'cooling_power'),
        ('DopplerCooling', 'detuning'),
        ('Transitions', 'main_cooling_369'),
        ('Deshelving', 'repump_power'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_760_1_freq'),
        ('ddsDefaults', 'repump_760_2_freq'),
        ('ddsDefaults', 'repump_976_freq'),
        ('ddsDefaults', 'repump_976_power'),
        ('ddsDefaults', 'DP369_freq')
    ]

    def sequence(self):
        p = self.parameters

        self.addDDS('369DP',
                    self.start,
                    p.VariableDeshelving.duration,
                    p.Transitions.main_cooling_369/2.0 + p.ddsDefaults.DP369_freq + p.DopplerCooling.detuning/2.0,
                    p.DopplerCooling.cooling_power)

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.VariableDeshelving.duration,
                    p.ddsDefaults.doppler_cooling_freq,
                    p.ddsDefaults.doppler_cooling_power)

        self.addDDS('935SP',
                    self.start,
                    p.VariableDeshelving.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.Deshelving.repump_power)

        self.addDDS('760SP',
                    self.start,
                    p.VariableDeshelving.duration,
                    p.ddsDefaults.repump_760_1_freq,
                    p.Deshelving.power1)

        self.addDDS('760SP2',
                    self.start,
                    p.VariableDeshelving.duration,
                    p.ddsDefaults.repump_760_2_freq,
                    p.Deshelving.power2)
        #
        # self.addDDS('976SP',
        #             self.start,
        #             p.VariableDeshelving.duration,
        #             p.ddsDefaults.repump_976_freq,
        #             p.ddsDefaults.repump_976_power)

        self.end = self.start + p.VariableDeshelving.duration
