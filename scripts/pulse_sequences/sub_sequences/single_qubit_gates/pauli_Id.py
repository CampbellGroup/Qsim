from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class PauliId(PulseSequence):
    required_parameters = [
        ("MicrowaveInterrogation", "power"),
        ("MicrowaveInterrogation", "ttl_switch_delay"),
        ("MicrowaveInterrogation", "overall_phase"),
        ("MicrowaveInterrogation", "microwave_source"),
        ("Transitions", "qubit_0"),
        ("ddsDefaults", "qubit_dds_freq"),
        ("ddsDefaults", "qubit_dds_x32_freq"),
        ("ddsDefaults", "qubit_dds_x32_power"),
        ("Pi_times", "qubit_0"),
    ]

    def sequence(self):
        p = self.parameters

        if p.MicrowaveInterrogation.microwave_source == "HP+DDS":
            pi_time = p.Pi_times.qubit_0
            self.end = self.start + pi_time

        elif p.MicrowaveInterrogation.microwave_source == "DDSx32":
            pi_time = p.Pi_times.qubit_0
            self.end = self.start + pi_time
