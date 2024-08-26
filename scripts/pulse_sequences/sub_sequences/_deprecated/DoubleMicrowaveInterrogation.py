from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.standard_pi_pulse import (
    StandardPiPulseClock,
)
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.standard_pi_pulse import (
    standard_pi_pulse_plus,
)
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.knill_pi_pulse import (
    KnillPiPulseClock,
)
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.knill_pi_pulse import (
    knill_pi_pulse_plus,
)
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.spin_echo_pi_pulse import (
    SpinEchoPiPulseClock,
)
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.spin_echo_pi_pulse import (
    spin_echo_pi_pulse_plus,
)


class double_microwave_sequence(PulseSequence):
    # this sequence is exclusively used for F = 1 manifold preparation, so we only want
    # to do Pi-pulses
    required_parameters = [
        ("MicrowaveInterrogation", "pulse_sequence"),
    ]

    required_subsequences = [
        StandardPiPulseClock,
        standard_pi_pulse_plus,
        KnillPiPulseClock,
        knill_pi_pulse_plus,
        StandardPiPulseClock,
        standard_pi_pulse_plus,
        SpinEchoPiPulseClock,
        spin_echo_pi_pulse_plus,
    ]

    def sequence(self):
        p = self.parameters

        if p.MicrowaveInterrogation.PulseSequence == "standard":
            self.add_sequence(StandardPiPulseClock)
            self.add_sequence(standard_pi_pulse_plus)

        elif p.MicrowaveInterrogation.PulseSequence == "knill":
            self.add_sequence(KnillPiPulseClock)
            self.add_sequence(knill_pi_pulse_plus)

        elif p.MicrowaveInterrogation.PulseSequence == "SpinEcho + KnillZeeman":
            self.add_sequence(SpinEchoPiPulseClock)
            self.add_sequence(knill_pi_pulse_plus)
