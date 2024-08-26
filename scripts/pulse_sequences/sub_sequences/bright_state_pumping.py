from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import (
    MicrowaveInterrogation,
)
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.Hadamard import (
    Hadamard,
)
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.microwave_sequence_standard_random_phase import (
    MicrowaveSequenceStandardRandomPhase,
)
from labrad.units import WithUnit as U


class BrightStatePumping(PulseSequence):
    required_parameters = [
        ("BrightStatePumping", "doppler_power"),
        ("BrightStatePumping", "repump_power"),
        ("BrightStatePumping", "detuning"),
        ("BrightStatePumping", "duration"),
        ("BrightStatePumping", "bright_prep_method"),
        ("BrightStatePumping", "microwave_phase_list"),
        ("BrightStatePumping", "start_with_Hadamard"),
        ("MicrowaveInterrogation", "repetitions"),
        ("MicrowaveInterrogation", "microwave_phase"),
        ("Transitions", "main_cooling_369"),
        ("ddsDefaults", "doppler_cooling_freq"),
        ("ddsDefaults", "doppler_cooling_power"),
        ("ddsDefaults", "repump_935_freq"),
        ("ddsDefaults", "repump_976_freq"),
        ("ddsDefaults", "repump_976_power"),
        ("Modes", "bright_state_pumping"),
    ]

    required_subsequences = [
        OpticalPumping,
        MicrowaveInterrogation,
        Hadamard,
        MicrowaveSequenceStandardRandomPhase,
    ]

    def sequence(self):
        p = self.parameters

        prep_method = p.Modes.bright_state_pumping
        laser_mode = p.Modes.laser_369

        if prep_method == "Doppler Cooling":
            if laser_mode == "FiberEOM":
                self.add_ttl(
                    "WindfreakSynthHDTTL", self.start, p["BrightStatePumping.duration"]
                )
                self.add_dds(
                    "369DP",
                    self.start,
                    p["BrightStatePumping.duration"],
                    p["Transitions.main_cooling_369"] / 2.0
                    + U(200.0, "MHz")
                    + p["BrightStatePumping.detuning"] / 2.0,
                    p["BrightStatePumping.doppler_power"],
                )
                self.add_dds(
                    "935SP",
                    self.start,
                    p["BrightStatePumping.duration"],
                    p["ddsDefaults.repump_935_freq"],
                    p["BrightStatePumping.repump_power"],
                )
                self.add_dds(
                    "976SP",
                    self.start,
                    p["BrightStatePumping.duration"],
                    p["ddsDefaults.repump_976_freq"],
                    p["ddsDefaults.repump_976_power"],
                )
                self.end = self.start + p.BrightStatePumping.duration

            elif laser_mode == "FiberEOM173":
                # self.addTTL('WindfreakSynthHDTTL',
                #             self.start,
                #             p["BrightStatePumping.duration"])
                self.add_dds(
                    "369DP",
                    self.start,
                    p["BrightStatePumping.duration"],
                    p["Transitions.main_cooling_369"] / 2.0
                    + U(200.0, "MHz")
                    + p["BrightStatePumping.detuning"] / 2.0,
                    p["BrightStatePumping.doppler_power"],
                )
                self.add_dds(
                    "935SP",
                    self.start,
                    p["BrightStatePumping.duration"],
                    p["ddsDefaults.repump_935_freq"],
                    p["BrightStatePumping.repump_power"],
                )
                self.add_dds(
                    "976SP",
                    self.start,
                    p["BrightStatePumping.duration"],
                    p["ddsDefaults.repump_976_freq"],
                    p["ddsDefaults.repump_976_power"],
                )
                self.end = self.start + p.BrightStatePumping.duration

            elif laser_mode == "Standard":
                self.add_dds(
                    "DopplerCoolingSP",
                    self.start,
                    p["BrightStatePumping.duration"],
                    p["ddsDefaults.doppler_cooling_freq"],
                    p["ddsDefaults.doppler_cooling_power"],
                )
                self.add_dds(
                    "369DP",
                    self.start,
                    p["BrightStatePumping.duration"],
                    p["Transitions.main_cooling_369"] / 2.0
                    + U(200.0, "MHz")
                    + p["BrightStatePumping.detuning"] / 2.0,
                    p["BrightStatePumping.doppler_power"],
                )
                self.add_dds(
                    "935SP",
                    self.start,
                    p["BrightStatePumping.duration"],
                    p["ddsDefaults.repump_935_freq"],
                    p["BrightStatePumping.repump_power"],
                )
                self.end = self.start + p.BrightStatePumping.duration

        elif prep_method == "Microwave":
            self.add_sequence(OpticalPumping)
            if p["BrightStatePumping.start_with_Hadamard"] == "On":
                print("adding Hadamard gate")
                self.add_sequence(Hadamard)
            if p["BrightStatePumping.microwave_phase_list"] == "constant":
                for i in range(int(p["MicrowaveInterrogation.repetitions"])):
                    self.add_sequence(MicrowaveInterrogation)
            elif p["BrightStatePumping.microwave_phase_list"] == "random":
                for i in range(int(p["MicrowaveInterrogation.repetitions"])):
                    self.add_sequence(MicrowaveSequenceStandardRandomPhase)
