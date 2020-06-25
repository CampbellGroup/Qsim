from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class triangle_microwave_ramp(pulse_sequence):

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
        p = self.parameters

        #  select which zeeman level to prepare
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0

        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus

        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterogation.detuning + center)
        ramp_rate = (46.0 + p.MicrowaveInterogation.power['dBm'])/(p.MicrowaveInterogation.duration['ms']/2.0)

        # accumulate the phase of the DDS and set the correct phase to match the phase at the end of the
        # first part of the ramp
        phase_ramp_down = DDS_freq['MHz']*p.MicrowaveInterogation.duration['us']/2.0

        # ramp up from off to the max power in half the allocated interrogation time
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterogation.duration/2.0,
                    DDS_freq,
                    U(-46.0, 'dBm'),
                    U(0.0, 'rad'),
                    U(0.0, 'MHz'),
                    U(ramp_rate, 'dB'))

        # ramp down from max power to off in half the allocated interrogation time
        self.addDDS('Microwave_qubit',
                    self.start + p.MicrowaveInterogation.duration/2.0,
                    p.MicrowaveInterogation.duration/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'rad'),
                    U(0.0, 'MHz'),
                    U(-ramp_rate, 'dB'))

        self.end = self.start + p.MicrowaveInterogation.duration
