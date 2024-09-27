from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence


class DoublePass369(PulseSequence):
    required_parameters = [
        ("DoublePass369", "duration"),
        ("DoublePass369", "power"),
        ("Transitions", "main_cooling_369"),
        ("ddsDefaults", "DP369_freq"),
    ]

    def sequence(self):
        p = self.parameters

        self.add_dds(
            "369DP",
            self.start,
            p["DoublePass369.duration"],
            p["Transitions.main_cooling_369"] / 2.0 + p["ddsDefaults.DP369_freq"],
            p["DoublePass369.power"],
        )

        self.end = self.start + p["DoublePass369.duration"]
