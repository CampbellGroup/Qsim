from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class shelving(PulseSequence):

    required_parameters = [
        ("Shelving", "duration"),
        ("Shelving", "power"),
        ("Shelving", "assist_power"),
        ("Shelving", "repump_power"),
        ("Transitions", "main_cooling_369"),
        ("DopplerCooling", "detuning"),
    ]

    def sequence(self):
        p = self.parameters
        self.add_dds(
            "369DP",
            self.start,
            p.Shelving.duration,
            p.Transitions.main_cooling_369 / 2.0
            + U(200.0, "MHz")
            + p.DopplerCooling.detuning / 2.0,
            p.Shelving.assist_power,
        )

        self.add_dds(
            "DopplerCoolingSP",
            self.start,
            p.Shelving.duration,
            U(110.0, "MHz"),
            U(-9.0, "dBm"),
        )

        self.add_dds(
            "935SP",
            self.start,
            p.Shelving.duration,
            U(320.0, "MHz"),
            p.Shelving.repump_power,
        )

        self.add_dds(
            "411DP", self.start, p.Shelving.duration, U(250.0, "MHz"), p.Shelving.power
        )

        self.add_ttl("411TTL", self.start, p.Shelving.duration)

        self.end = self.start + p.Shelving.duration
