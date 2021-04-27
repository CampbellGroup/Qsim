from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.KnillSequence import knill
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.MicrowaveSequenceStandard import microwave_sequence_standard
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.BB1Sequence import bb1
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.SpinEchoSequence import spin_echo
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.SuMicrowaveSequence import su_sequence

from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.standard_pi_pulse import standard_pi_pulse_clock
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.standard_pi_pulse import standard_pi_pulse_plus
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.standard_pi_pulse import standard_pi_pulse_minus

from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.knill_pi_pulse import knill_pi_pulse_clock
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.knill_pi_pulse import knill_pi_pulse_plus
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.knill_pi_pulse import knill_pi_pulse_minus

from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.spin_echo_pi_pulse import spin_echo_pi_pulse_clock
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.spin_echo_pi_pulse import spin_echo_pi_pulse_plus
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.spin_echo_pi_pulse import spin_echo_pi_pulse_minus

class microwave_interrogation(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'pulse_sequence'),
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
                             spin_echo, su_sequence,
                             standard_pi_pulse_plus, standard_pi_pulse_clock, standard_pi_pulse_minus,
                             knill_pi_pulse_plus, knill_pi_pulse_clock, knill_pi_pulse_minus,
                             spin_echo_pi_pulse_plus, spin_echo_pi_pulse_clock, spin_echo_pi_pulse_minus]

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

        elif p.MicrowaveInterrogation.pulse_sequence == 'SuSequence':
            self.addSequence(su_sequence)

        elif p.MicrowaveInterrogation.pulse_sequence == 'DoubleStandard':
            self.addSequence(standard_pi_pulse_clock)
            self.addSequence(standard_pi_pulse_minus)

        elif p.MicrowaveInterrogation.pulse_sequence == 'DoubleKnill':
            self.addSequence(knill_pi_pulse_clock)
            self.addSequence(knill_pi_pulse_minus)

        elif p.MicrowaveInterrogation.pulse_sequence == 'DoubleSpinEcho':
            self.addSequence(spin_echo_pi_pulse_clock)
            self.addSequence(spin_echo_pi_pulse_minus)

        elif p.MicrowaveInterrogation.pulse_sequence == 'ClockStandard_KnillZeeman':
            self.addSequence(standard_pi_pulse_clock)
            self.addSequence(knill_pi_pulse_minus)

        elif p.MicrowaveInterrogation.pulse_sequence == 'TripleMicrowave':
            self.addSequence(knill_pi_pulse_clock)
            self.addSequence(knill_pi_pulse_minus)
            self.addSequence(knill_pi_pulse_plus)

