from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class state_detection(pulse_sequence):

    required_parameters = [
                           ('StateReadout', 'duration'),
                           ('StateReadout', 'CW_power'),
                           ('StateReadout', 'ML_power'),
                           ('StateReadout', 'repump_power'),
                           ('StateReadout', 'detuning'),
                           ('StateReadout', 'mode'),
                           ('Transitions', 'main_cooling_369')
                           ]

    def sequence(self):
        p = self.parameters

        self.addDDS('repump',
                    self.start,
                    p.StateReadout.duration,
                    U(320.0, 'MHz'),
                    p.StateReadout.repump_power)

        self.addTTL('935EOM', self.start, p.StateReadout.duration)

        if p.StateReadout.mode == 'CW':
            self.addDDS('State Detection',
                        self.start,
                        p.StateReadout.duration,
                        U(110.0, 'MHz'),
                        p.StateReadout.CW_power)

            self.addDDS('369',
                        self.start,
                        p.StateReadout.duration,
                        p.Transitions.main_cooling_369 + p.StateReadout.detuning,
                        U(-5.0, 'dBm'))

        elif p.StateReadout.mode == 'ML':
            self.addDDS('ML_SinglePass',
                        self.start,
                        p.StateReadout.duration,
                        U(320.0, 'MHz'),
                        p.StateReadout.ML_power)

        self.addTTL('ReadoutCount',
                    self.start,
                    p.StateReadout.duration)
        self.end = self.start + p.StateReadout.duration