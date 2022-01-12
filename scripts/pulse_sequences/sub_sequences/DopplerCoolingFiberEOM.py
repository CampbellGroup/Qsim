from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class doppler_cooling_fiber_eom(pulse_sequence):

    required_parameters = [
        ('DopplerCooling', 'cooling_power'),
        ('DopplerCooling', 'repump_power'),
        ('DopplerCooling', 'detuning'),
        ('DopplerCooling', 'duration'),
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
        ('ddsDefaults', 'DP369_freq'),
                           ]

    def sequence(self):
        p = self.parameters

        # self.addTTL('WindfreakSynthHDTTL',
        #            self.start,
        #            p.DopplerCooling.duration)

        self.addDDS('369DP',
                    self.start,
                    p.DopplerCooling.duration,
                    p.Transitions.main_cooling_369/2.0 + p.ddsDefaults.DP369_freq + p.DopplerCooling.detuning/2.0,
                    p.DopplerCooling.cooling_power)

        self.addDDS('935SP',
                    self.start,
                    p.DopplerCooling.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.DopplerCooling.repump_power)

        self.addDDS('976SP',
                    self.start,
                    p.DopplerCooling.duration,
                    p.ddsDefaults.repump_976_freq,
                    p.ddsDefaults.repump_976_power)

        self.addDDS('760SP',
                    self.start,
                    p.DopplerCooling.duration,
                    p.ddsDefaults.repump_760_1_freq,
                    p.ddsDefaults.repump_760_1_power)

        self.addDDS('760SP2',
                    self.start,
                    p.DopplerCooling.duration,
                    p.ddsDefaults.repump_760_2_freq,
                    p.ddsDefaults.repump_760_2_power)

        self.end = self.start + p.DopplerCooling.duration
