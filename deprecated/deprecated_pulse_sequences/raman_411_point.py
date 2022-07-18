from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from scripts.pulse_sequences.sub_sequences.doppler_cooling import DopplerCooling
from deprecated.deprecated_sub_sequences.Raman411Interogation import raman_411_interogation
from scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import microwave_interogation
from scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping


class raman_411_point(pulse_sequence):

    required_subsequences = [TurnOffAll, DopplerCooling, raman_411_interogation,
                             StandardStateDetection, OpticalPumping, microwave_interogation]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(TurnOffAll)
        self.addSequence(DopplerCooling)
        self.addSequence(OpticalPumping)
        self.addSequence(microwave_interogation)
        self.addSequence(raman_411_interogation)
        self.addSequence(microwave_interogation)
        self.addSequence(StandardStateDetection)
