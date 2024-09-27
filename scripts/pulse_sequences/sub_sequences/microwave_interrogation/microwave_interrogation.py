from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.knill_sequence import (
    Knill,
)
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.MicrowaveSequenceStandard import (
    MicrowaveSequenceStandard,
)
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.bb1_sequence import (
    BB1,
)
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.spin_echo_sequence import (
    SpinEcho,
)
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.su_microwave_sequence import (
    SuSequence,
)

from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.standard_pi_pulse import (
    StandardPiPulseClock,
)
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.standard_pi_pulse import (
    standard_pi_pulse_plus,
)
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.standard_pi_pulse import (
    standard_pi_pulse_minus,
)

from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.knill_pi_pulse import (
    KnillPiPulseClock,
)
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.knill_pi_pulse import (
    knill_pi_pulse_plus,
)
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.knill_pi_pulse import (
    knill_pi_pulse_minus,
)

from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.spin_echo_pi_pulse import (
    SpinEchoPiPulseClock,
)
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.spin_echo_pi_pulse import (
    spin_echo_pi_pulse_plus,
)
from Qsim.scripts.pulse_sequences.sub_sequences.pi_pulses.spin_echo_pi_pulse import (
    spin_echo_pi_pulse_minus,
)


class MicrowaveInterrogation(PulseSequence):
    required_parameters = [
        ("MicrowaveInterrogation", "duration"),
        ("MicrowaveInterrogation", "detuning"),
        ("MicrowaveInterrogation", "power"),
        ("MicrowaveInterrogation", "pulse_sequence"),
        ("MicrowaveInterrogation", "AC_line_trigger"),
        ("MicrowaveInterrogation", "delay_from_line_trigger"),
        ("Line_Selection", "qubit"),
        ("Transitions", "qubit_0"),
        ("Transitions", "qubit_plus"),
        ("Transitions", "qubit_minus"),
        ("Pi_times", "qubit_0"),
        ("Pi_times", "qubit_plus"),
        ("Pi_times", "qubit_minus"),
        ("MicrowaveInterrogation", "repetitions"),
    ]
    required_subsequences = [
        Knill,
        MicrowaveSequenceStandard,
        BB1,
        SpinEcho,
        SuSequence,
        standard_pi_pulse_plus,
        StandardPiPulseClock,
        standard_pi_pulse_minus,
        knill_pi_pulse_plus,
        KnillPiPulseClock,
        knill_pi_pulse_minus,
        spin_echo_pi_pulse_plus,
        SpinEchoPiPulseClock,
        spin_echo_pi_pulse_minus,
    ]

    def sequence(self):
        p = self.parameters

        if p["MicrowaveInterrogation.pulse_sequence"] == "standard":
            self.add_sequence(MicrowaveSequenceStandard)

        elif p["MicrowaveInterrogation.pulse_sequence"] == "knill":
            self.add_sequence(Knill)

        elif p["MicrowaveInterrogation.pulse_sequence"] == "BB1":
            self.add_sequence(BB1)

        elif p["MicrowaveInterrogation.pulse_sequence"] == "SpinEcho":
            self.add_sequence(SpinEcho)

        elif p["MicrowaveInterrogation.pulse_sequence"] == "SuSequence":
            self.add_sequence(SuSequence)

        elif p["MicrowaveInterrogation.pulse_sequence"] == "DoubleStandard":
            self.add_sequence(StandardPiPulseClock)
            self.add_sequence(standard_pi_pulse_minus)

        elif p["MicrowaveInterrogation.pulse_sequence"] == "DoubleKnill":
            self.add_sequence(KnillPiPulseClock)
            self.add_sequence(knill_pi_pulse_minus)

        elif p["MicrowaveInterrogation.pulse_sequence"] == "DoubleSpinEcho":
            self.add_sequence(SpinEchoPiPulseClock)
            self.add_sequence(spin_echo_pi_pulse_minus)

        elif p["MicrowaveInterrogation.pulse_sequence"] == "ClockStandard_KnillZeeman":
            self.add_sequence(StandardPiPulseClock)
            self.add_sequence(knill_pi_pulse_minus)

        elif p["MicrowaveInterrogation.pulse_sequence"] == "TripleMicrowave":
            self.add_sequence(KnillPiPulseClock)
            self.add_sequence(knill_pi_pulse_minus)
            self.add_sequence(knill_pi_pulse_plus)
