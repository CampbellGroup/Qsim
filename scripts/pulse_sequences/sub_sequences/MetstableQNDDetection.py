from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class metastable_qnd_detection(pulse_sequence):

    required_parameters = [
        ('MetastableStateDetection', 'duration'),
        ('MetastableStateDetection', 'repump_power'),
        ('MetastableStateDetection', 'detuning'),
        ('MetastableStateDetection', 'CW_power'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'DP369_freq')
    ]

    def sequence(self):
        p = self.parameters

        # first we deshelve the F=3 manifold

        self.addTTL('976SP',
                    self.start,
                    p.MetastableStateDetection.duration)

        self.addDDS('935SP',
                    self.start,
                    p.MetastableStateDetection.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.MetastableStateDetection.repump_power)

        self.addTTL('ReadoutCount',
                    self.start,
                    p.MetastableStateDetection.duration)

        self.addDDS('369DP',
                    self.start,
                    p.MetastableStateDetection.duration,
                    p.Transitions.main_cooling_369/2.0 + p.ddsDefaults.DP369_freq + p.MetastableStateDetection.detuning/2.0,
                    p.MetastableStateDetection.CW_power)

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.MetastableStateDetection.duration,
                    p.ddsDefaults.doppler_cooling_freq,
                    p.ddsDefaults.doppler_cooling_power)

        self.end = self.start + p.MetastableStateDetection.duration
