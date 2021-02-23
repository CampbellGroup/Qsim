from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class metastable_state_detection(pulse_sequence):

    required_parameters = [
        ('MetastableStateDetection', 'duration'),
        ('MetastableStateDetection', 'repump_power'),
        ('MetastableStateDetection', 'detuning'),
        ('MetastableStateDetection', 'CW_power'),
        ('MetastableStateDetection', 'deshelving_duration'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_760_1_freq'),
        ('ddsDefaults', 'repump_760_1_power'),
        ('ddsDefaults', 'DP369_freq'),
        ('ddsDefaults', 'repump_976_power'),
        ('ddsDefaults', 'repump_976_freq')
    ]

    def sequence(self):
        p = self.parameters

        # first we deshelve the F=3 manifold

        self.addDDS('760SP',
                    self.start,
                    p.MetastableStateDetection.deshelving_duration,
                    p.ddsDefaults.repump_760_1_freq,
                    p.ddsDefaults.repump_760_1_power)

        self.addDDS('976SP',
                    self.start,
                    p.MetastableStateDetection.deshelving_duration + p.MetastableStateDetection.duration,
                    p.ddsDefaults.repump_976_freq,
                    p.ddsDefaults.repump_976_power)

        self.addDDS('935SP',
                    self.start,
                    p.MetastableStateDetection.duration + p.MetastableStateDetection.deshelving_duration,
                    p.ddsDefaults.repump_935_freq,
                    p.MetastableStateDetection.repump_power)

        self.addTTL('ReadoutCount',
                    self.start + p.MetastableStateDetection.deshelving_duration,
                    p.MetastableStateDetection.duration)

        self.addDDS('369DP',
                    self.start,
                    p.MetastableStateDetection.duration + p.MetastableStateDetection.deshelving_duration,
                    p.Transitions.main_cooling_369/2.0 + p.ddsDefaults.DP369_freq + p.MetastableStateDetection.detuning/2.0,
                    p.MetastableStateDetection.CW_power)

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.MetastableStateDetection.duration + p.MetastableStateDetection.deshelving_duration,
                    p.ddsDefaults.doppler_cooling_freq,
                    p.ddsDefaults.doppler_cooling_power)

        self.end = self.start + p.MetastableStateDetection.duration + p.MetastableStateDetection.deshelving_duration
