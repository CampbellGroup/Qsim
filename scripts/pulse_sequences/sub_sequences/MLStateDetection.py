from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class ml_state_detection(pulse_sequence):

    required_parameters = [
                           ('MLStateDetection', 'ML_power'),
                           ('MLStateDetection', 'duration'),
                           ('MLStateDetection', 'repump_power'),
                           ('Transitions', 'main_cooling_369'),
                            ]

    def sequence(self):
        p = self.parameters

        self.addTTL('ReadoutCount',
                    self.start,
                    p.MLStateDetection.duration)

        self.addDDS('935SP',
                    self.start,
                    p.MLStateDetection.duration,
                    U(320.0, 'MHz'),
                    p.MLStateDetection.repump_power)

#        self.addDDS('ModeLockedSP',
#                    self.start,
#                    p.MLStateDetection.duration,
#                    U(200.0, 'MHz'),
#                    p.MLStateDetection.ML_power)

        self.addDDS('369DP',
                    self.start,
                    p.MLStateDetection.duration,
                    U(200.0, 'MHz'),
                    U(-46.0, 'dBm'))

        self.addTTL('TimeHarpPMT',
                    self.start,
                    p.MLStateDetection.duration)

        self.end = self.start + p.MLStateDetection.duration
