from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class zeeman_bright_optical_pumping(pulse_sequence):

    required_parameters = [
                           ('ZeemanPumping', 'duration'),
                           ('ZeemanPumping', 'power'),
                           ('Transitions', 'zeeman_pumping_plus'),
                           ('Transitions', 'zeeman_pumping_minus')
                           ]

    def sequence(self):
        p = self.parameters
        print p.Transitions.zeeman_pumping_minus
        print p.Transitions.zeeman_pumping_plus
        self.addDDS('411DP',
                    self.start,
                    p.ZeemanPumping.duration,
                    U(250.0, 'MHz') + p.Transitions.zeeman_pumping_plus/2.0,
                    p.ZeemanPumping.power)

        self.addDDS('760SP',
                    self.start,
                    p.ZeemanPumping.duration,
                    U(160.0, 'MHz'),
                    U(-2.0, 'dBm'))

        self.addTTL('976SP',
                    self.start,
                    p.ZeemanPumping.duration)

        self.end = self.start + p.ZeemanPumping.duration


class zeeman_dark_optical_pumping(pulse_sequence):

    required_parameters = [
                           ('ZeemanPumping', 'duration'),
                           ('ZeemanPumping', 'power'),
                           ('Transitions', 'zeeman_pumping_plus'),
                           ('Transitions', 'zeeman_pumping_minus')
                           ]

    def sequence(self):
        p = self.parameters

        self.addDDS('411DP',
                    self.start,
                    p.ZeemanPumping.duration,
                    U(250.0, 'MHz') + p.Transitions.zeeman_pumping_minus/2.0,
                    p.ZeemanPumping.power)

        self.addDDS('760SP',
                    self.start,
                    p.ZeemanPumping.duration,
                    U(160.0, 'MHz'),
                    U(-7.0, 'dBm'))

        self.addTTL('976SP',
                    self.start,
                    p.ZeemanPumping.duration)

        self.end = self.start + p.ZeemanPumping.duration
