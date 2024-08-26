from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class CoherenceMeasurementMicrowaveSequence(PulseSequence):
    required_parameters = [
        ("MicrowaveInterrogation", "power"),
        ("MicrowaveInterrogation", "ttl_switch_delay"),
        ("Transitions", "qubit_0"),
        ("ddsDefaults", "qubit_dds_freq"),
        ("EmptySequence", "duration"),
        ("Pi_times", "qubit_0"),
        ("CoherenceMeasurement", "target_end_state"),
        ("CoherenceMeasurement", "delay_times"),
    ]

    def sequence(self):
        p = self.parameters

        center = p.Transitions.qubit_0
        pi_time = p.Pi_times.qubit_0

        DDS_freq = p.ddsDefaults.qubit_dds_freq - center
        pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay

        # first pi/2 pulse, DDS turns on 800 us before the ttl allows it through
        self.add_ttl("MicrowaveTTL", self.start + pulse_delay, pi_time / 2.0)
        self.add_dds(
            "Microwave_qubit",
            self.start,
            pi_time / 2.0 + pulse_delay,
            DDS_freq,
            p.MicrowaveInterrogation.power,
            U(0.0, "deg"),
        )

        self.add_ttl(
            "MicrowaveTTL",
            self.start + pulse_delay + p.EmptySequence.duration / 2.0 + pi_time / 2.0,
            pi_time,
        )
        self.add_dds(
            "Microwave_qubit",
            self.start + pi_time / 2.0 + p.EmptySequence.duration / 2.0,
            pi_time + pulse_delay,
            DDS_freq,
            p.MicrowaveInterrogation.power,
            U(0.0, "deg"),
        )

        if p.CoherenceMeasurement.target_end_state == "Zero":
            self.add_ttl(
                "MicrowaveTTL",
                self.start
                + 3.0 * pi_time / 2.0
                + p.EmptySequence.duration
                + pulse_delay,
                pi_time / 2.0,
            )
            self.add_dds(
                "Microwave_qubit",
                self.start + 3.0 * pi_time / 2.0 + p.EmptySequence.duration,
                pi_time / 2.0 + pulse_delay,
                DDS_freq,
                p.MicrowaveInterrogation.power,
                U(0.0, "deg"),
            )

        elif p.CoherenceMeasurement.target_end_state == "One":
            self.add_ttl(
                "MicrowaveTTL",
                self.start
                + 3.0 * pi_time / 2.0
                + p.EmptySequence.duration
                + pulse_delay,
                pi_time / 2.0,
            )
            self.add_dds(
                "Microwave_qubit",
                self.start + 3.0 * pi_time / 2.0 + p.EmptySequence.duration,
                pi_time / 2.0 + pulse_delay,
                DDS_freq,
                p.MicrowaveInterrogation.power,
                U(180.0, "deg"),
            )

        self.end = self.start + 2.0 * pi_time + p.EmptySequence.duration + pulse_delay
