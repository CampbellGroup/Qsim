from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class shelving_state_detection(pulse_sequence):

    required_parameters = [
                           ('ShelvingStateDetection', 'duration'),
                           ('ShelvingStateDetection', 'repump_power'),
                           ('ShelvingStateDetection', 'detuning'),
                           ('ShelvingStateDetection', 'CW_power'),
                           ('ShelvingStateDetection', 'state_detection_laser'),
                           ('Transitions', 'main_cooling_369'),
                           ('Deshelving', 'duration'),
                           ('Deshelving', 'power'),
                           ('ShelvingStateDetection', 'protection_cooling_duration'),
                           ('ShelvingStateDetection', 'protection_cooling_detuning'),
                           ('ShelvingStateDetection', 'protection_cooling_power'),
                            ]

    def sequence(self):
        p = self.parameters
        detection_laser = p.ShelvingStateDetection.state_detection_laser
        protection_cooling_duration = p.ShelvingStateDetection.protection_cooling_duration
        protection_cooling_detuning = p.ShelvingStateDetection.protection_cooling_detuning
        protection_cooling_power = p.ShelvingStateDetection.protection_cooling_power
        total_duration = p.ShelvingStateDetection.duration + protection_cooling_duration
        self.addTTL('ReadoutCount',
                    self.start,
                    total_duration)

        self.addDDS('935SP',
                    self.start,
                    total_duration,
                    U(320.0, 'MHz'),
                    p.ShelvingStateDetection.repump_power)

        if detection_laser == 'DopplerCooling':

            self.addDDS('369DP',
                        self.start,
                        protection_cooling_duration,
                        p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + protection_cooling_detuning/2.0,
                        protection_cooling_power)

            self.addDDS('369DP',
                        self.start + protection_cooling_duration,
                        p.ShelvingStateDetection.duration,
                        p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.ShelvingStateDetection.detuning/2.0,
                        p.ShelvingStateDetection.CW_power)

            self.addDDS('DopplerCoolingSP',
                        self.start,
                        total_duration,
                        U(110.0, 'MHz'),
                        U(-20.8, 'dBm'))

        elif detection_laser == 'ML':
            self.addDDS('ModeLockedSP',
                        self.start,
                        p.ShelvingStateDetection.duration,
                        U(200.0, 'MHz'),
                        p.ShelvingStateDetection.CW_power)
            self.addTTL('TimeHarpPMT',
                        self.start,
                        p.ShelvingStateDetection.duration)

        self.addDDS('760SP',
                    self.start + U(10.0, 'us') + total_duration,
                    p.Deshelving.duration,
                    U(320.0, 'MHz'),
                    p.Deshelving.power)

        self.end = self.start + total_duration + U(10.0, 'us') + p.Deshelving.duration
