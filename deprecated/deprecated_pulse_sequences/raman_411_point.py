from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from scripts.pulse_sequences.sub_sequences.DopplerCooling import doppler_cooling
from deprecated.deprecated_sub_sequences.Raman411Interogation import raman_411_interogation
from scripts.pulse_sequences.sub_sequences.TurnOffAll import turn_off_all
from scripts.pulse_sequences.sub_sequences.StandardStateDetection import standard_state_detection
from scripts.pulse_sequences.sub_sequences.MicrowaveInterrogation import microwave_interogation
from scripts.pulse_sequences.sub_sequences.OpticalPumping import optical_pumping


class raman_411_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling, raman_411_interogation,
                             standard_state_detection, optical_pumping, microwave_interogation]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(microwave_interogation)
        self.addSequence(raman_411_interogation)
        self.addSequence(microwave_interogation)
        self.addSequence(standard_state_detection)
