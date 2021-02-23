from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.standard_pi_pulse import standard_pi_pulse_clock
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.standard_pi_pulse import standard_pi_pulse_plus
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.knill_pi_pulse import knill_pi_pulse_clock
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.knill_pi_pulse import knill_pi_pulse_plus
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.spin_echo_pi_pulse import spin_echo_pi_pulse_clock
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.spin_echo_pi_pulse import spin_echo_pi_pulse_plus



class double_microwave_sequence(pulse_sequence):
    # this sequence is exclusively used for F = 1 manifold preparation, so we only want
    # to do Pi-pulses
    required_parameters = [
                           ('MicrowaveInterrogation', 'pulse_sequence'),
                           ]

    required_subsequences = [standard_pi_pulse_clock, standard_pi_pulse_plus, knill_pi_pulse_clock,
                             knill_pi_pulse_plus, standard_pi_pulse_clock, standard_pi_pulse_plus,
                             spin_echo_pi_pulse_clock, spin_echo_pi_pulse_plus]

    def sequence(self):
        p = self.parameters

        if p.MicrowaveInterrogation.pulse_sequence == 'standard':
            self.addSequence(standard_pi_pulse_clock)
            self.addSequence(standard_pi_pulse_plus)

        elif p.MicrowaveInterrogation.pulse_sequence == 'knill':
            self.addSequence(knill_pi_pulse_clock)
            self.addSequence(knill_pi_pulse_plus)

        elif p.MicrowaveInterrogation.pulse_sequence == 'SpinEcho + KnillZeeman':
            self.addSequence(spin_echo_pi_pulse_clock)
            self.addSequence(knill_pi_pulse_plus)
