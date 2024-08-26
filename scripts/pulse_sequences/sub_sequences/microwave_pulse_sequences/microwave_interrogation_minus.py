from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class MicrowaveInterrogationMinus(PulseSequence):
    required_parameters = [
        ("MicrowaveInterrogation", "duration"),
        ("MicrowaveInterrogation", "detuning"),
        ("MicrowaveInterrogation", "power"),
        ("MicrowaveInterrogation", "microwave_phase"),
        ("MicrowaveInterrogation", "ttl_switch_delay"),
        ("Transitions", "qubit_minus"),
        ("ddsDefaults", "qubit_dds_freq"),
    ]

    def sequence(self):
        p = self.parameters

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (
            p.MicrowaveInterrogation.detuning + p.Transitions.qubit_minus
        )
        pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay

        self.add_ttl(
            "MicrowaveTTL", self.start + pulse_delay, p.MicrowaveInterrogation.duration
        )
        self.add_dds(
            "Microwave_qubit",
            self.start,
            p.MicrowaveInterrogation.duration + pulse_delay,
            DDS_freq,
            p.MicrowaveInterrogation.power,
            p.MicrowaveInterrogation.microwave_phase,
        )

        self.end = self.start + p.MicrowaveInterrogation.duration + pulse_delay
