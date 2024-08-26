from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class MetastableRamseyMicrowaveInterrogation(PulseSequence):
    required_parameters = [
        ("MetastableMicrowaveRamsey", "detuning"),
        ("MetastableMicrowaveRamsey", "cooling_lasers_during_microwaves"),
        ("Metastable_Microwave_Interrogation", "microwave_phase"),
        ("DopplerCooling", "cooling_power"),
        ("DopplerCooling", "repump_power"),
        ("DopplerCooling", "detuning"),
        ("Transitions", "MetastableQubit"),
        ("ddsDefaults", "metastable_qubit_dds_freq"),
        ("ddsDefaults", "metastable_qubit_dds_power"),
        ("ddsDefaults", "doppler_cooling_freq"),
        ("ddsDefaults", "doppler_cooling_power"),
        ("ddsDefaults", "repump_935_freq"),
        ("ddsDefaults", "repump_935_power"),
        ("EmptySequence", "duration"),
        ("Pi_times", "metastable_qubit"),
        ("Transitions", "main_cooling_369"),
    ]

    def sequence(self):
        p = self.parameters

        center = p.Transitions.MetastableQubit
        pi_time = p.Pi_times.metastable_qubit

        DDS_freq = (
            p.ddsDefaults.metastable_qubit_dds_freq
            + (p.MetastableMicrowaveRamsey.detuning + center) / 8.0
        )

        self.add_dds(
            "3GHz_qubit",
            self.start,
            pi_time / 2.0,
            DDS_freq,
            p.ddsDefaults.metastable_qubit_dds_power,
            U(0.0, "deg"),
        )

        self.add_dds(
            "3GHz_qubit",
            self.start + pi_time / 2.0 + p.EmptySequence.duration,
            pi_time / 2.0,
            DDS_freq,
            p.ddsDefaults.metastable_qubit_dds_power,
            p.Metastable_Microwave_Interrogation.microwave_phase / 8.0,
        )

        if p.MetastableMicrowaveRamsey.cooling_lasers_during_microwaves == "On":
            self.add_dds(
                "935SP",
                self.start + pi_time / 2.0,
                p.EmptySequence.duration,
                p.ddsDefaults.repump_935_freq,
                p.ddsDefaults.repump_935_power,
            )

            self.add_dds(
                "369DP",
                self.start + pi_time / 2.0,
                p.EmptySequence.duration,
                p.Transitions.main_cooling_369 / 2.0
                + U(200.0, "MHz")
                + p.DopplerCooling.detuning / 2.0,
                U(-4.0, "dBm"),
            )

            self.add_dds(
                "DopplerCoolingSP",
                self.start + pi_time / 2.0,
                p.EmptySequence.duration,
                p.ddsDefaults.doppler_cooling_freq,
                p.ddsDefaults.doppler_cooling_power,
            )

        self.end = self.start + pi_time + p.EmptySequence.duration
