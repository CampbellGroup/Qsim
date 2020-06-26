from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.KnillSequence import knill
from Qsim.scripts.pulse_sequences.sub_sequences.MicrowaveSequenceStandard import microwave_sequence_standard
from Qsim.scripts.pulse_sequences.sub_sequences.BB1Sequence import bb1
from Qsim.scripts.pulse_sequences.sub_sequences.SpinEchoSequence import spin_echo
from Qsim.scripts.pulse_sequences.sub_sequences.KnillPulseAreaCorrective import knill_pulse_area_correcting_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.AdiabaticRapidPassageMicrowave import adiabatic_rapid_passage_microwave


class microwave_interrogation(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'pulse_sequence'),
        ('MicrowaveInterrogation', 'ARP_sweep_time'),
        ('MicrowaveInterrogation', 'ARP_freq_span'),
        ('MicrowaveInterrogation', 'AC_line_trigger'),
        ('MicrowaveInterrogation', 'delay_from_line_trigger'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Transitions', 'qubit_plus'),
        ('Transitions', 'qubit_minus'),
        ('Pi_times', 'qubit_0'),
        ('Pi_times', 'qubit_plus'),
        ('Pi_times', 'qubit_minus'),
        ('MicrowaveInterrogation', 'repetitions')
    ]
    required_subsequences = [knill, microwave_sequence_standard, bb1,
                             spin_echo, knill_pulse_area_correcting_sequence,
                             adiabatic_rapid_passage_microwave]

    def sequence(self):
        p = self.parameters

        if p.MicrowaveInterrogation.pulse_sequence == 'standard':
            self.addSequence(microwave_sequence_standard)

        elif p.MicrowaveInterrogation.pulse_sequence == 'knill':
            self.addSequence(knill)

        elif p.MicrowaveInterrogation.pulse_sequence == 'BB1':
            self.addSequence(bb1)

        elif p.MicrowaveInterrogation.pulse_sequence == 'SpinEcho':
            self.addSequence(spin_echo)

        elif p.MicrowaveInterrogation.pulse_sequence == 'KnillPulseAreaCorrecting':
            self.addSequence(knill_pulse_area_correcting_sequence)

        elif p.MicrowaveInterrogation.pulse_sequence == 'ARP':
            self.addSequence(adiabatic_rapid_passage_microwave)
