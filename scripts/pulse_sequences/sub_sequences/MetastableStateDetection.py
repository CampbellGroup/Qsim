from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class metastable_state_detection(pulse_sequence):

    required_parameters = [
                           ('MetastableStateDetection', 'duration'),
                           ('MetastableStateDetection', 'repump_power'),
                           ('MetastableStateDetection', 'detuning'),
                           ('MetastableStateDetection', 'CW_power'),
                           ('Deshelving', 'power1'),
                           ('Transitions', 'main_cooling_369'),
                            ]

    def sequence(self):
        p = self.parameters

        self.addTTL('ReadoutCount',
                    self.start,
                    p.MetastableStateDetection.duration)

        self.addDDS('935SP',
                    self.start,
                    p.MetastableStateDetection.duration,
                    U(320.0, 'MHz'),
                    p.MetastableStateDetection.repump_power)

        self.addDDS('369DP',
                    self.start,
                    p.MetastableStateDetection.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.MetastableStateDetection.detuning/2.0,
                    p.MetastableStateDetection.CW_power)

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.MetastableStateDetection.duration,
                    U(110.0, 'MHz'),
                    U(-9.0, 'dBm'))

        self.addDDS('760SP',
                    self.start,
                    p.MetastableStateDetection.duration,
                    U(160.0, 'MHz'),
                    p.Deshelving.power1)

        self.end = self.start + p.MetastableStateDetection.duration
