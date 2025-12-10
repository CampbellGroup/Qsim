from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from Qsim.scripts.pulse_sequences.sub_sequences.metastable_microwave_sequence_standard import (
    MetastableMicrowaveSequenceStandard,
)
from Qsim.scripts.pulse_sequences.sub_sequences.metastable_microwave_knill_sequence import (
    MetastableMicrowaveKnillSequence,
)


class MetastableMicrowaveInterrogation(PulseSequence):
    required_parameters = [
        ("Metastable_Microwave_Interrogation", "duration"),
        ("Metastable_Microwave_Interrogation", "detuning"),
        ("Metastable_Microwave_Interrogation", "power"),
        ("Metastable_Microwave_Interrogation", "pulse_sequence"),
        ("Transitions", "MetastableQubit"),
        ("ddsDefaults", "metastable_qubit_dds_freq"),
        ("ddsDefaults", "metastable_qubit_dds_power"),
    ]

    required_subsequences = [
        MetastableMicrowaveSequenceStandard,
        MetastableMicrowaveKnillSequence,
    ]

    def sequence(self):
        p = self.parameters

        if p["Metastable_Microwave_Interrogation.pulse_sequence"] == "Standard":
            self.add_sequence(MetastableMicrowaveSequenceStandard)

        if p["Metastable_Microwave_Interrogation.pulse_sequence"] == "Knill":
            self.add_sequence(MetastableMicrowaveKnillSequence)
