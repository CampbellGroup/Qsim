from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class adiabatic_rapid_passage_microwave(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterogation', 'detuning'),
        ('MicrowaveInterogation', 'power'),
        ('MicrowaveInterogation', 'ARP_freq_span'),
        ('MicrowaveInterogation', 'ARP_sweep_time'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Transitions', 'qubit_plus'),
        ('Transitions', 'qubit_minus'),
        ('ddsDefaults', 'qubit_dds_freq')
        ]

    def sequence(self):
        p = self.parameters

        #  select which zeeman level to prepare
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0

        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus

        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterogation.detuning + center)

        freq_range = p.MicrowaveInterogation.ARP_freq_span['MHz']
        sweep_time = p.MicrowaveInterogation.ARP_sweep_time['ms']
        freq_sweep_rate = freq_range/sweep_time

        self.addDDS('Microwave_qubit',
                    self.start,
                    U(1.0, 'us'),
                    DDS_freq - U(freq_range, 'MHz') / 2.0,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg'),
                    U(0.0, 'MHz'),
                    U(0.0, 'dB'))

        self.addDDS('Microwave_qubit',
                    self.start + U(1.0, 'us'),
                    p.MicrowaveInterogation.ARP_sweep_time,
                    DDS_freq + U(freq_range, 'MHz')/2.0,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg'),
                    U(freq_sweep_rate, 'MHz'),
                    U(0.0, 'dB'))

        self.end = self.start + p.MicrowaveInterogation.ARP_sweep_time + U(1.0, 'us')
