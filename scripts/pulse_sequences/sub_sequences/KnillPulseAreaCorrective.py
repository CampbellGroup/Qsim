from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class knill_pulse_area_correcting_sequence(pulse_sequence):
    """
    This is a knill sequence with variable pulse area and detuning
    """

    required_parameters = [
                           ('MicrowaveInterogation', 'duration'),
                           ('MicrowaveInterogation', 'detuning'),
                           ('MicrowaveInterogation', 'power'),
                           ('Line_Selection', 'qubit'),
                           ('Transitions', 'qubit_0'),
                           ('Transitions', 'qubit_plus'),
                           ('Transitions', 'qubit_minus'),
                           ('ddsDefaults', 'qubit_dds_freq')
                           ]

    def sequence(self):
        """
        This sequence is based on the work by David Su, a modification of the Knill sequence that sacrifices
        correcting detuning errors for correcting amplitude errors.
        """
        p = self.parameters

        #  select which zeeman level to prepare
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0

        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus

        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterogation.detuning + center)
        alpha = U(180.0, 'deg')

        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterogation.duration,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(30.0, 'deg') - 2*alpha)
        self.addDDS('Microwave_qubit',
                    self.start + p.MicrowaveInterogation.duration,
                    p.MicrowaveInterogation.duration,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg') - alpha)
        self.addDDS('Microwave_qubit',
                    self.start + 2*p.MicrowaveInterogation.duration,
                    p.MicrowaveInterogation.duration,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(90.0, 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + 3*p.MicrowaveInterogation.duration,
                    p.MicrowaveInterogation.duration,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg') + alpha)
        self.addDDS('Microwave_qubit',
                    self.start + 4*p.MicrowaveInterogation.duration,
                    p.MicrowaveInterogation.duration,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(30.0, 'deg') + 2*alpha)
        self.end = self.start + 5*p.MicrowaveInterogation.duration
