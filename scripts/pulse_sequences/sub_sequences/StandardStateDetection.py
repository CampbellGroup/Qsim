from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class standard_state_detection(pulse_sequence):

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
        ('ddsDefaults', 'DP369_freq')
    ]

    def sequence(self):
        p = self.parameters

        if p.StandardStateDetection.method == 'Standard':
            self.addTTL('ReadoutCount',
                        self.start,
                        p.StandardStateDetection.duration)
            self.addDDS('935SP',
                        self.start,
                        p.StandardStateDetection.duration,
                        p.ddsDefaults.repump_935_freq,
                        p.StandardStateDetection.repump_power)
            self.addDDS('StateDetectionSP',
                        self.start,
                        p.StandardStateDetection.duration,
                        p.ddsDefaults.state_detection_freq,
                        p.ddsDefaults.state_detection_power)
            self.addDDS('369DP',
                        self.start,
                        p.StandardStateDetection.duration,
                        p.Transitions.main_cooling_369/2.0 + p.ddsDefaults.DP369_freq + p.StandardStateDetection.detuning/2.0,
                        p.StandardStateDetection.CW_power)
            self.end = self.start + p.StandardStateDetection.duration

        if p.StandardStateDetection.method == 'StandardFiberEOM':
            self.addDDS('369DP',
                        self.start,
                        p.DopplerCooling.duration,
                        p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq + p.DopplerCooling.detuning / 2.0,
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
