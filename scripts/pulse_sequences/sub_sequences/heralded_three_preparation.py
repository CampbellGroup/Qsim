from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence


class HeraldedThreePreparation(PulseSequence):
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
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_760_2_freq'),
        ('ddsDefaults', 'repump_760_2_power'),
        ('ddsDefaults', 'repump_976_freq'),
        ('ddsDefaults', 'repump_976_power'),
        ('ddsDefaults', 'metastable_qubit_dds_freq'),
        ('ddsDefaults', 'metastable_qubit_dds_power'),
        ('ddsDefaults', 'DP369_freq'),
        ('ddsDefaults', 'protection_beam_freq'),
        ('ddsDefaults', 'protection_beam_power'),
    ]

    def sequence(self):
        p = self.parameters
        qubitFreq = p.ddsDefaults.metastable_qubit_dds_freq + p.Transitions.MetastableQubit / 8.0

        self.add_ttl('ReadoutCount',
                     self.start + p.Pi_times.metastable_qubit + p.HeraldedStatePreparation.deshelving_duration,
                     p.MetastableStateDetection.duration)

        # perform pi pulse on the desired transition
        self.add_dds('3GHz_qubit',
                     self.start,
                     p.Pi_times.metastable_qubit,
                     qubitFreq,
                     p.ddsDefaults.metastable_qubit_dds_power)

        # deshelve population in the F = 4 manifold that is left over from poor Pi Pulse
        self.add_dds('760SP2',
                     self.start + p.Pi_times.metastable_qubit,
                     p.HeraldedStatePreparation.deshelving_duration + p.MetastableStateDetection.duration,
                     p.ddsDefaults.repump_760_2_freq,
                     p.ddsDefaults.repump_760_2_power)

        # detect any population in the ground state, at first here we will use the state detection parameters
        self.add_dds('935SP',
                     self.start,
                     p.MetastableStateDetection.duration + p.Pi_times.metastable_qubit + p.HeraldedStatePreparation.deshelving_duration,
                     p.ddsDefaults.repump_935_freq,
                     p.MetastableStateDetection.repump_power)

        self.add_dds('976SP',
                     self.start,
                     p.Pi_times.metastable_qubit + p.HeraldedStatePreparation.deshelving_duration + p.MetastableStateDetection.duration,
                     p.ddsDefaults.repump_976_freq,
                     p.ddsDefaults.repump_976_power)

        self.add_dds('369DP',
                     self.start + p.Pi_times.metastable_qubit,
                     p.MetastableStateDetection.duration + p.HeraldedStatePreparation.deshelving_duration,
                     p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq + p.MetastableStateDetection.detuning / 2.0,
                     p.MetastableStateDetection.CW_power)

        self.add_dds('DopplerCoolingSP',
                     self.start + p.Pi_times.metastable_qubit,
                     p.MetastableStateDetection.duration + p.HeraldedStatePreparation.deshelving_duration,
                     p.ddsDefaults.doppler_cooling_freq,
                     p.ddsDefaults.doppler_cooling_power)

        self.add_dds('ProtectionBeam',
                     self.start + p.Pi_times.metastable_qubit,
                     p.HeraldedStatePreparation.deshelving_duration + p.MetastableStateDetection.duration,
                     p.ddsDefaults.protection_beam_freq,
                     p.ddsDefaults.protection_beam_power)

        self.end = self.start + p.Pi_times.metastable_qubit + p.HeraldedStatePreparation.deshelving_duration + p.MetastableStateDetection.duration
