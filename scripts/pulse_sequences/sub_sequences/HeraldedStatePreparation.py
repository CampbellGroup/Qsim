from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class heralded_state_preparation(pulse_sequence):

    required_parameters = [
                           ('MetastableStateDetection', 'duration'),
                           ('MetastableStateDetection', 'repump_power'),
                           ('MetastableStateDetection', 'detuning'),
                           ('MetastableStateDetection', 'CW_power'),
                           ('Deshelving', 'power1'),
                           ('Transitions', 'main_cooling_369'),
                           ('Transitions', 'MetastableQubit'),
                           ('Pi_times', 'metastable_qubit'),
                           ('HeraldedStatePreparation', 'deshelving_duration'),
                            ]

    def sequence(self):
        p = self.parameters
        qubitFreq = U(270.000, 'MHz') - p.Transitions.MetastableQubit

        self.addTTL('ReadoutCount',
                    self.start + p.Pi_times.metastable_qubit + p.HeraldedStatePreparation.deshelving_duration,
                    p.MetastableStateDetection.duration)

        # perform pi pulse on the desired transition
        self.addDDS('3GHz_qubit',
                    self.start,
                    p.Pi_times.metastable_qubit,
                    qubitFreq,
                    U(-11.0, 'dBm'))

        # deshelve any remaining population in the original manifold
        self.addDDS('760SP',
                    self.start + p.Pi_times.metastable_qubit,
                    p.HeraldedStatePreparation.deshelving_duration,
                    U(160.0, 'MHz'),
                    U(-2.0, 'dBm'))

        # detect any population in the ground state, at first here we will use the state detection parameters
        self.addDDS('935SP',
                    self.start + p.Pi_times.metastable_qubit + p.HeraldedStatePreparation.deshelving_duration,
                    p.MetastableStateDetection.duration,
                    U(320.0, 'MHz'),
                    p.MetastableStateDetection.repump_power)

        self.addDDS('369DP',
                    self.start + p.Pi_times.metastable_qubit + p.HeraldedStatePreparation.deshelving_duration,
                    p.MetastableStateDetection.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.MetastableStateDetection.detuning/2.0,
                    p.MetastableStateDetection.CW_power)

        self.addDDS('DopplerCoolingSP',
                    self.start + p.Pi_times.metastable_qubit + p.HeraldedStatePreparation.deshelving_duration,
                    p.MetastableStateDetection.duration,
                    U(110.0, 'MHz'),
                    U(-9.0, 'dBm'))

        self.end = self.start + p.Pi_times.metastable_qubit + p.HeraldedStatePreparation.deshelving_duration + p.MetastableStateDetection.duration