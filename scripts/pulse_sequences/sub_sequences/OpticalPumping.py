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
                           ('Transitions', 'main_cooling_369'),
                           ('DopplerCooling', 'detuning'),
    ]

    def sequence(self):
        p = self.parameters
        opMethod = p.OpticalPumping.method

        if opMethod == 'Standard':
            self.addDDS('OpticalPumpingSP',
                        self.start,
                        p.OpticalPumping.duration,
                        U(110.0, 'MHz'),
                        U(-4.0, 'dBm'))

            self.addDDS('369DP',
                        self.start,
                        p.OpticalPumping.duration,
                        p.Transitions.main_cooling_369/2 + U(200.0, 'MHz') + p.OpticalPumping.detuning/2.0,
                        p.OpticalPumping.power)

            self.addDDS('935SP',
                        self.start,
                        p.OpticalPumping.duration,
                        U(320.0, 'MHz'),
                        p.OpticalPumping.repump_power)

            self.addDDS('760SP',
                        self.start,
                        p.OpticalPumping.duration,
                        U(160.0, 'MHz'),
                        U(-2.0,  'dBm'))

            self.end = self.start + p.OpticalPumping.duration

        if opMethod == 'QuadrupoleOnly':
            self.addDDS('935SP',
                        self.start,
                        p.OpticalPumping.quadrupole_op_duration,
                        U(320.0, 'MHz'),
                        p.OpticalPumping.repump_power)

            self.addDDS('760SP',
                        self.start,
                        p.OpticalPumping.quadrupole_op_duration,
                        U(160.0, 'MHz'),
                        U(-2.0,  'dBm'))

            self.addDDS('760SP2',
                        self.start,
                        p.OpticalPumping.quadrupole_op_duration,
                        U(160.0, 'MHz'),
                        U(6.0,  'dBm'))

            self.addDDS('411DP',
                        self.start,
                        p.OpticalPumping.quadrupole_op_duration,
                        U(200.0, 'MHz') + p.OpticalPumping.quadrupole_op_detuning,
                        U(-6.8, 'dBm'))

            self.addTTL('976SP',
                        self.start,
                        p.OpticalPumping.quadrupole_op_duration)

            self.end = self.start + p.OpticalPumping.quadrupole_op_duration

        if opMethod == 'Both':
            self.addDDS('OpticalPumpingSP',
                        self.start,
                        p.OpticalPumping.duration,
                        U(110.0, 'MHz'),
                        U(-4.0, 'dBm'))

            self.addDDS('369DP',
                        self.start,
                        p.OpticalPumping.duration,
                        p.Transitions.main_cooling_369/2 + U(200.0, 'MHz') + p.OpticalPumping.detuning/2.0,
                        p.OpticalPumping.power)

            self.addDDS('935SP',
                        self.start,
                        p.OpticalPumping.duration + p.OpticalPumping.quadrupole_op_duration,
                        U(320.0, 'MHz'),
                        p.OpticalPumping.repump_power)

            self.addDDS('760SP',
                        self.start,
                        p.OpticalPumping.duration + p.OpticalPumping.quadrupole_op_duration,
                        U(160.0, 'MHz'),
                        U(-2.0,  'dBm'))

            self.addDDS('760SP2',
                        self.start,
                        p.OpticalPumping.duration + p.OpticalPumping.quadrupole_op_duration,
                        U(160.0, 'MHz'),
                        U(6.0,  'dBm'))

            self.addDDS('411DP',
                        self.start + p.OpticalPumping.duration,
                        p.OpticalPumping.quadrupole_op_duration,
                        U(200.0, 'MHz') + p.OpticalPumping.quadrupole_op_detuning,
                        U(-6.8, 'dBm'))

            self.addTTL('976SP',
                        self.start,
                        p.OpticalPumping.quadrupole_op_duration + p.OpticalPumping.duration)

            self.end = self.start + p.OpticalPumping.duration + p.OpticalPumping.quadrupole_op_duration
