from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.KnillMicrowaveSequence import knill_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.MicrowaveSequenceStandard import microwave_sequence_standard
from Qsim.scripts.pulse_sequences.sub_sequences.BB1MicrowaveSequence import bb1_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.SpinEchoSequence import spin_echo_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.KnillPulseAreaCorrective import knill_pulse_area_correcting_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.AdiabaticRapidPassageMicrowave import adiabatic_rapid_passage_microwave


class microwave_interogation(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterogation', 'duration'),
        ('MicrowaveInterogation', 'detuning'),
        ('MicrowaveInterogation', 'power'),
        ('MicrowaveInterogation', 'pulse_sequence'),
        ('MicrowaveInterogation', 'ARP_sweep_time'),
        ('MicrowaveInterogation', 'ARP_freq_span'),
        ('MicrowaveInterogation', 'AC_line_trigger'),
        ('MicrowaveInterrogation', 'delay_from_line_trigger'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Transitions', 'qubit_plus'),
        ('Transitions', 'qubit_minus'),
        ('Pi_times', 'qubit_0'),
        ('Pi_times', 'qubit_plus'),
        ('Pi_times', 'qubit_minus'),
        ('MicrowaveInterogation', 'repititions')
    ]
    required_subsequences = [knill_sequence, microwave_sequence_standard, bb1_sequence,
                             spin_echo_sequence, knill_pulse_area_correcting_sequence,
                             adiabatic_rapid_passage_microwave]

    def sequence(self):
        p = self.parameters

        if p.MicrowaveInterogation.pulse_sequence == 'standard':
            self.addSequence(microwave_sequence_standard)

        elif p.MicrowaveInterogation.pulse_sequence == 'knill':
            self.addSequence(knill_sequence)

        elif p.MicrowaveInterogation.pulse_sequence == 'BB1':
            self.addSequence(bb1_sequence)

        elif p.MicrowaveInterogation.pulse_sequence == 'SpinEcho':
            self.addSequence(spin_echo_sequence)

        elif p.MicrowaveInterogation.pulse_sequence == 'KnillPulseAreaCorrecting':
            self.addSequence(knill_pulse_area_correcting_sequence)

        elif p.MicrowaveInterogation.pulse_sequence == 'ARP':
            self.addSequence(adiabatic_rapid_passage_microwave)
