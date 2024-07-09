from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.doppler_cooling import DopplerCooling
from .sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from .sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from .sub_sequences.turn_off_all import TurnOffAll
from .sub_sequences.bright_state_pumping import BrightStatePumping
from .sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from .sub_sequences.shelving import Shelving
from .sub_sequences.deshelving import Deshelving
from .sub_sequences.optical_pumping import OpticalPumping
from .sub_sequences.microwave_interrogation.microwave_interrogation import MicrowaveInterrogation


class BrightStatePreparation(PulseSequence):

    required_subsequences = [DopplerCooling, StandardStateDetection,
                             ShelvingStateDetection, TurnOffAll, BrightStatePumping,
                             ShelvingDopplerCooling, Shelving, Deshelving, OpticalPumping,
                             MicrowaveInterrogation]
    required_parameters = [
        ('Modes', 'state_detection_mode')]

    def sequence(self):

        state_detection_mode = self.parameters.Modes.state_detection_mode

        # standard bright state is the 1 state
        if state_detection_mode == 'Standard':
            self.add_sequence(TurnOffAll)
            self.add_sequence(DopplerCooling)
            self.add_sequence(BrightStatePumping)
            self.add_sequence(StandardStateDetection)

        # shelving bright state is the 0 state
        elif state_detection_mode == 'Shelving':
            self.add_sequence(TurnOffAll)
            self.add_sequence(ShelvingDopplerCooling)
            self.add_sequence(OpticalPumping)
            self.add_sequence(Shelving)
            self.add_sequence(ShelvingStateDetection)
            self.add_sequence(Deshelving)
