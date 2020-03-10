from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class knill_sequence_minus(pulse_sequence):
    """
    This is a fixed Pi-pulse subsequence
    """

    required_parameters = [
                           ('MicrowaveInterogation', 'duration'),
                           ('MicrowaveInterogation', 'detuning'),
                           ('MicrowaveInterogation', 'power'),
                           ('Transitions', 'qubit_minus'),
                           ('Pi_times', 'qubit_minus'),
                           ('ddsDefaults', 'qubit_dds_freq')
                           ]

    def sequence(self):
        p = self.parameters

        #  just prepares the mF = -1 state 
        center = p.Transitions.qubit_minus
        pi_time = p.Pi_times.qubit_minus
        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterogation.detuning + center)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(30.0, 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + pi_time,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + 2*pi_time,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(90.0, 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + 3*pi_time,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + 4*pi_time,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(30.0, 'deg'))
        self.end = self.start + 5*pi_time
