from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class standard_state_detection(pulse_sequence):

    required_parameters = [
                           ('StandardStateDetection', 'duration'),
                           ('StandardStateDetection', 'CW_power'),
                           ('StandardStateDetection', 'repump_power'),
                           ('StandardStateDetection', 'detuning'),
                           ('Transitions', 'main_cooling_369'),
                            ]

    def sequence(self):
        p = self.parameters

        self.addTTL('ReadoutCount',
                    self.start,
                    p.StandardStateDetection.duration)

        self.addDDS('935SP',
                    self.start,
                    p.StandardStateDetection.duration,
                    U(320.0, 'MHz'),
                    p.StandardStateDetection.repump_power)

        self.addDDS('StateDetectionSP',
                    self.start,
                    p.StandardStateDetection.duration,
                    U(110.0 + 6.7, 'MHz'),
                    U(-18.7, 'dBm'))

        self.addDDS('369DP',
                    self.start,
                    p.StandardStateDetection.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0 - 6.7/2.0, 'MHz') + p.StandardStateDetection.detuning/2.0,
                    p.StandardStateDetection.CW_power)

        self.end = self.start + p.StandardStateDetection.duration
