from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class MicrowaveSequenceStandardHpOnly(PulseSequence):
    # this sequence is for when we use the DDS as a reference for the HP and
    # want to keep it on at all times, we will not change the oscillator frequency

    required_parameters = [
        ("MicrowaveInterrogation", "duration"),
        ("Line_Selection", "qubit"),
        ("Transitions", "qubit_0"),
        ("Transitions", "qubit_plus"),
        ("Transitions", "qubit_minus"),
        ("ddsDefaults", "qubit_dds_freq"),
    ]

    def sequence(self):
        p = self.parameters
        # buffer time is there so that when we concatenate pulses, the ttl will turn off for sure and
        # then turn back on for the next pi pulse

        buffer_time = U(2000.0, "us")
        self.add_ttl(
            "MicrowaveTTL", self.start + buffer_time, p.MicrowaveInterrogation.duration
        )

        self.end = self.start + p.MicrowaveInterrogation.duration + buffer_time
