from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class SFDiscriminationDetection(PulseSequence):
    required_parameters = [
        ("SF_Discrimination", "cooling_power"),
        ("DopplerCooling", "repump_power"),
        ("SF_Discrimination", "detuning"),
        ("SF_Discrimination", "detection_duration"),
        ("Transitions", "main_cooling_369"),
        ("ddsDefaults", "doppler_cooling_freq"),
        ("ddsDefaults", "doppler_cooling_power"),
        ("ddsDefaults", "repump_935_freq"),
        ("ddsDefaults", "repump_760_1_freq"),
        ("ddsDefaults", "repump_760_1_power"),
        ("ddsDefaults", "repump_760_2_freq"),
        ("ddsDefaults", "repump_760_2_power"),
        ("ddsDefaults", "DP369_freq"),
    ]

    def sequence(self):
        p = self.parameters

        self.add_dds(
            "DopplerCoolingSP",
            self.start,
            p.SF_Discrimination.detection_duration,
            p.ddsDefaults.doppler_cooling_freq,
            p.ddsDefaults.doppler_cooling_power,
        )

        self.add_dds(
            "369DP",
            self.start,
            p.SF_Discrimination.detection_duration,
            p.Transitions.main_cooling_369 / 2.0
            + p.ddsDefaults.DP369_freq
            + p.SF_Discrimination.detuning / 2.0,
            p.SF_Discrimination.cooling_power,
        )

        self.add_dds(
            "935SP",
            self.start,
            p.SF_Discrimination.detection_duration,
            p.ddsDefaults.repump_935_freq,
            p.DopplerCooling.repump_power,
        )

        self.add_ttl("ReadoutCount", self.start, p.SF_Discrimination.detection_duration)

        self.end = self.start + p.SF_Discrimination.detection_duration
