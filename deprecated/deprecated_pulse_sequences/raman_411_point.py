from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from scripts.pulse_sequences.sub_sequences.doppler_cooling import doppler_cooling
from deprecated.deprecated_sub_sequences.Raman411Interogation import raman_411_interogation
from scripts.pulse_sequences.sub_sequences.turn_off_all import turn_off_all
from scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import standard_state_detection
from scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import microwave_interogation
from scripts.pulse_sequences.sub_sequences.optical_pumping import optical_pumping


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
