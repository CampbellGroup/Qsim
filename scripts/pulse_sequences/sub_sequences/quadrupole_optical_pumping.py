from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class OpticalPumping(PulseSequence):

    required_parameters = [
        ('QuadrupoleOpticalPumping', 'duration'),
        ('QuadrupoleOpticalPumping', 'power'),
        ('QuadrupoleOpticalPumping', 'detuning'),
        ('QuadrupoleOpticalPumping', 'repump_power'),
        ('QuadrupoleOpticalPumping', 'method'),
        ('QuadrupoleOpticalPumping', 'quadrupole_op_duration'),
        ('QuadrupoleOpticalPumping', 'quadrupole_op_detuning'),
        ('QuadrupoleOpticalPumping', 'extra_repump_time'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'optical_pumping_freq'),
        ('ddsDefaults', 'optical_pumping_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_760_1_freq'),
        ('ddsDefaults', 'repump_760_1_power'),
        ('ddsDefaults', 'repump_760_2_freq'),
        ('ddsDefaults', 'repump_760_2_power'),
        ('ddsDefaults', 'DP369_freq'),
        ('ddsDefaults', 'DP2_411_power'),
        ('ddsDefaults', 'DP2_411_freq'),
        ('ddsDefaults', 'repump_976_freq'),
        ('ddsDefaults', 'repump_976_power')
    ]

    def sequence(self):
        p = self.parameters

        self.add_dds('935SP',
                     self.start,
                     p.QuadrupoleOpticalPumping.duration + p.QuadrupoleOpticalPumping.extra_repump_time,
                     p.ddsDefaults.repump_935_freq,
                     p.QuadrupoleOpticalPumping.repump_power)
        self.add_dds('760SP',
                     self.start,
                     p.QuadrupoleOpticalPumping.duration + p.QuadrupoleOpticalPumping.extra_repump_time,
                     p.ddsDefaults.repump_760_1_freq,
                     p.ddsDefaults.repump_760_1_power)
        self.add_dds('760SP2',
                     self.start,
                     p.QuadrupoleOpticalPumping.duration + p.QuadrupoleOpticalPumping.extra_repump_time,
                     p.ddsDefaults.repump_760_2_freq,
                     p.ddsDefaults.repump_760_2_power)
        self.add_dds('411DP2',
                     self.start,
                     p.QuadrupoleOpticalPumping.duration,
                     p.ddsDefaults.DP2_411_freq,
                     p.ddsDefaults.DP2_411_power)
        self.add_dds('976SP',
                     self.start,
                     p.QuadrupoleOpticalPumping.duration + p.QuadrupoleOpticalPumping.extra_repump_time,
                     p.ddsDefaults.repump_976_freq,
                     p.ddsDefaults.repump_976_power)
        self.end = self.start + p.QuadrupoleOpticalPumping.duration + p.QuadrupoleOpticalPumping.extra_repump_time
