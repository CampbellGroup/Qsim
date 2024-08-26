from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class ml_state_detection(PulseSequence):

    required_parameters = [
                           ('MLStateDetection', 'ML_power'),
                           ('MLStateDetection', 'duration'),
                           ('MLStateDetection', 'repump_power'),
                           ('Transitions', 'main_cooling_369'),
                            ]

    def sequence(self):
        p = self.parameters

        self.add_ttl('ReadoutCount',
                     self.start,
                     p.MLStateDetection.duration)

        self.add_dds('935SP',
                     self.start,
                     p.MLStateDetection.duration,
                     U(320.0, 'MHz'),
                     p.MLStateDetection.repump_power)

#        self.addDDS('ModeLockedSP',
#                    self.start,
#                    p.MLStateDetection.duration,
#                    U(200.0, 'MHz'),
#                    p.MLStateDetection.ML_power)

        self.add_dds('369DP',
                     self.start,
                     p.MLStateDetection.duration,
                     U(200.0, 'MHz'),
                     U(-46.0, 'dBm'))

        self.add_ttl('TimeHarpPMT',
                     self.start,
                     p.MLStateDetection.duration)

        self.end = self.start + p.MLStateDetection.duration
