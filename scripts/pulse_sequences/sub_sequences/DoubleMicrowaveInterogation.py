from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from Qsim.scripts.pulse_sequences.sub_sequences.MicrowaveSequenceStandard import microwave_sequence_standard
from Qsim.scripts.pulse_sequences.sub_sequences.KnillMicrowaveSequence import knill_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.SpinEchoSequence import spin_echo_sequence

class double_microwave_sequence(pulse_sequence):

    required_parameters = [
                           ('MicrowaveInterogation', 'duration'),
                           ('MicrowaveInterogation', 'detuning'),
                           ('MicrowaveInterogation', 'power'),
                           ('MicrowaveInterogation', 'pulse_sequence'),
                           ('Line_Selection', 'qubit'),
                           ('Transitions', 'qubit_0'),
                           ('Transitions', 'qubit_plus'),
                           ('Transitions', 'qubit_minus'),
                           ('Pi_times', 'qubit_0'),
                           ('Pi_times', 'qubit_plus'),
                           ('ddsDefaults', 'qubit_dds_freq')
                           ]

    required_subsequences = [microwave_sequence_standard, knill_sequence, spin_echo_sequence]

    def sequence(self):
        p = self.parameters

        pi_time_0 = p.Pi_times.qubit_0
        pi_time_plus = p.Pi_times.qubit_plus


        if p.MicrowaveInterogation.pulse_sequence == 'standard':
            # set the pi time and line selection parameter for first Pi pulse
            p['MicrowaveInterogation.duration'] = pi_time_0
            p['Line_Selection.qubit'] = 'qubit_0'
            self.addSequence(microwave_sequence_standard)

            # set the pi time and line selection parameter for second Pi pulse
            p['MicrowaveInterogation.duration'] = pi_time_plus
            p['Line_Selection.qubit'] = 'qubit_plus'
            self.addSequence(microwave_sequence_standard)

        elif p.MicrowaveInterogation.pulse_sequence == 'knill':
            # set the pi time and line selection parameter for first Pi pulse
            p['MicrowaveInterogation.duration'] = pi_time_0
            p['Line_Selection.qubit'] = 'qubit_0'
            self.addSequence(knill_sequence)

            # set the pi time and line selection parameter for second Pi pulse
            p['MicrowaveInterogation.duration'] = pi_time_plus
            p['Line_Selection.qubit'] = 'qubit_plus'
            self.addSequence(knill_sequence)

        elif p.MicrowaveInterogation.pulse_sequence == 'SpinEcho + KnillZeeman':
            # set the pi time and line selection parameter for first Pi pulse
            p['MicrowaveInterogation.duration'] = pi_time_0
            p['Line_Selection.qubit'] = 'qubit_0'
            self.addSequence(spin_echo_sequence)

            # set the pi time and line selection parameter for second Pi pulse
            p['MicrowaveInterogation.duration'] = pi_time_plus
            p['Line_Selection.qubit'] = 'qubit_plus'
            self.addSequence(knill_sequence)