from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class state_detection(pulse_sequence):

    required_parameters = [
                           ('StateDetection', 'duration'),
                           ('StateDetection', 'CW_power'),
                           ('StateDetection', 'ML_power'),
                           ('StateDetection', 'repump_power'),
                           ('StateDetection', 'detuning'),
                           ('StateDetection', 'mode'),
                           ('DopplerCooling', 'cooling_power'),
                           ('DopplerCooling', 'detuning'),
                           ('Transitions', 'main_cooling_369')
                            ]

    def sequence(self):
        p = self.parameters

        self.addDDS('935SP',
                    self.start,
                    p.StateDetection.duration,
                    U(320.0, 'MHz'),
                    p.StateDetection.repump_power)

        if p.StateDetection.mode == 'CW':

            self.addTTL('935EOM', self.start, p.StateDetection.duration)

            self.addDDS('StateDetectionSP',
                        self.start,
                        p.StateDetection.duration,
                        U(110.0, 'MHz'),
                        p.StateDetection.CW_power)

            self.addDDS('369DP',
                        self.start,
                        p.StateDetection.duration,
                        p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.StateDetection.detuning,
                        U(-5.0, 'dBm'))

        elif p.StateDetection.mode == 'ML':
            self.addDDS('ModeLockedSP',
                        self.start,
                        p.StateDetection.duration,
                        U(320.0, 'MHz'),
                        p.StateDetection.ML_power)

            self.addDDS('369DP',
                        self.start,
                        p.StateDetection.duration,
                        U(200.0, 'MHz'),
                        U(-46.0, 'dBm'))

        elif p.StateDetection.mode == 'Shelving':

            self.addDDS('DopplerCoolingSP',
                        self.start,
                        p.StateDetection.duration,
                        U(110.0, 'MHz'),
                        p.DopplerCooling.cooling_power)

            self.addDDS('369DP',
                        self.start,
                        p.StateDetection.duration,
                        p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
                        U(-5.0, 'dBm'))


        self.addTTL('ReadoutCount',
                    self.start,
                    p.StateDetection.duration)
        self.end = self.start + p.StateDetection.duration
