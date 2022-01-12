from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class optical_pumping(pulse_sequence):

    required_parameters = [
        ('OpticalPumping', 'duration'),
        ('OpticalPumping', 'power'),
        ('OpticalPumping', 'detuning'),
        ('OpticalPumping', 'repump_power'),
        ('OpticalPumping', 'method'),
        ('OpticalPumping', 'quadrupole_op_duration'),
        ('OpticalPumping', 'quadrupole_op_detuning'),
        ('OpticalPumping', 'extra_repump_time'),
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
        opMethod = p.OpticalPumping.method

        if opMethod == 'Standard':
            self.addDDS('OpticalPumpingSP',
                        self.start,
                        p.OpticalPumping.duration,
                        p.ddsDefaults.optical_pumping_freq,
                        p.ddsDefaults.optical_pumping_power)
            # extra 5 Mhz shift on the double pass to reflect the different frequency for the OP AOM
            # as compared to the DC and SD AOMs
            self.addDDS('369DP',
                        self.start,
                        p.OpticalPumping.duration,
                        p.Transitions.main_cooling_369/2.0 + p.ddsDefaults.DP369_freq + p.OpticalPumping.detuning/2.0 - U(5.0, 'MHz'),
                        p.OpticalPumping.power)
            self.addDDS('935SP',
                        self.start,
                        p.OpticalPumping.duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_935_freq,
                        p.OpticalPumping.repump_power)
            self.addDDS('760SP',
                        self.start,
                        p.OpticalPumping.duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_760_1_freq,
                        p.ddsDefaults.repump_760_1_power)
            self.addDDS('760SP2',
                        self.start,
                        p.OpticalPumping.duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_760_2_freq,
                        p.ddsDefaults.repump_760_2_power)
            self.end = self.start + p.OpticalPumping.duration + p.OpticalPumping.extra_repump_time

        elif opMethod == 'StandardFiberEOM':
            self.addTTL('WindfreakSynthNVTTL',
                        self.start,
                        p.OpticalPumping.duration)
            self.addTTL('WindfreakSynthHDTTL',
                       self.start,
                       p.OpticalPumping.duration)
            self.addDDS('369DP',
                        self.start,
                        p.OpticalPumping.duration,
                        p.Transitions.main_cooling_369/2.0 + p.ddsDefaults.DP369_freq,#  + p.OpticalPumping.detuning/2.0,
                        p.OpticalPumping.power)
            self.addDDS('935SP',
                        self.start,
                        p.OpticalPumping.duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_935_freq,
                        p.OpticalPumping.repump_power)
            self.addDDS('760SP',
                        self.start,
                        p.OpticalPumping.duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_760_1_freq,
                        p.ddsDefaults.repump_760_1_power)
            self.addDDS('760SP2',
                        self.start,
                        p.OpticalPumping.duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_760_2_freq,
                        p.ddsDefaults.repump_760_2_power)
            self.end = self.start + p.OpticalPumping.duration + p.OpticalPumping.extra_repump_time

        if opMethod == 'QuadrupoleOnly':
            self.addDDS('935SP',
                        self.start,
                        p.OpticalPumping.quadrupole_op_duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_935_freq,
                        p.OpticalPumping.repump_power)
            self.addDDS('760SP',
                        self.start,
                        p.OpticalPumping.quadrupole_op_duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_760_1_freq,
                        p.ddsDefaults.repump_760_1_power)
            self.addDDS('760SP2',
                        self.start,
                        p.OpticalPumping.quadrupole_op_duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_760_2_freq,
                        p.ddsDefaults.repump_760_2_power)
            self.addDDS('411DP2',
                        self.start,
                        p.OpticalPumping.quadrupole_op_duration,
                        p.ddsDefaults.DP2_411_freq,
                        p.ddsDefaults.DP2_411_power)
            self.addDDS('976SP',
                        self.start,
                        p.OpticalPumping.quadrupole_op_duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_976_freq,
                        p.ddsDefaults.repump_976_power)
            self.end = self.start + p.OpticalPumping.quadrupole_op_duration + p.OpticalPumping.extra_repump_time

        elif opMethod == 'Both':
            self.addDDS('OpticalPumpingSP',
                        self.start,
                        p.OpticalPumping.duration,
                        p.ddsDefaults.optical_pumping_freq,
                        p.ddsDefaults.optical_pumping_power)
            self.addDDS('369DP',
                        self.start,
                        p.OpticalPumping.duration,
                        p.Transitions.main_cooling_369/2.0 + p.ddsDefaults.DP369_freq + p.OpticalPumping.detuning/2.0 - U(5.0, 'MHz'),
                        p.OpticalPumping.power)
            self.addDDS('935SP',
                        self.start,
                        p.OpticalPumping.duration + p.OpticalPumping.quadrupole_op_duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_935_freq,
                        p.OpticalPumping.repump_power)
            self.addDDS('760SP',
                        self.start,
                        p.OpticalPumping.duration + p.OpticalPumping.quadrupole_op_duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_760_1_freq,
                        p.ddsDefaults.repump_760_1_power)
            self.addDDS('760SP2',
                        self.start,
                        p.OpticalPumping.duration + p.OpticalPumping.quadrupole_op_duration + p.OpticalPumping.extra_repump_time,
                        p.ddsDefaults.repump_760_2_freq,
                        p.ddsDefaults.repump_760_2_power)
            self.addDDS('411DP2',
                        self.start + p.OpticalPumping.duration,
                        p.OpticalPumping.quadrupole_op_duration,
                        p.ddsDefaults.DP2_411_freq,
                        p.ddsDefaults.DP2_411_power)
            self.addDDS('976SP',
                        self.start + p.OpticalPumping.duration,
                        p.OpticalPumping.quadrupole_op_duration,
                        p.ddsDefaults.repump_976_freq,
                        p.ddsDefaults.repump_976_power)
            self.end = self.start + p.OpticalPumping.duration + p.OpticalPumping.quadrupole_op_duration + p.OpticalPumping.extra_repump_time
