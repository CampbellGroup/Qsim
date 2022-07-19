from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import DopplerCooling
from sub_sequences.turn_off_all import TurnOffAll
from sub_sequences.optical_pumping import OpticalPumping
from sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from sub_sequences.microwave_interrogation.microwave_interrogation import MicrowaveInterrogation
from sub_sequences.bright_state_pumping import BrightStatePumping
from sub_sequences.shelving import Shelving
from sub_sequences.deshelving import Deshelving


class DarkStatePreparation(pulse_sequence):

    required_subsequences = [TurnOffAll, DopplerCooling, StandardStateDetection,
                             ShelvingStateDetection, OpticalPumping, Shelving, ShelvingDopplerCooling,
                             Deshelving, BrightStatePumping, MicrowaveInterrogation]

    required_parameters = [
        ('Modes', 'state_detection_mode'),
        ('BrightStatePumping', 'start_with_Hadamard')]

    def sequence(self):

        mode = self.parameters.Modes.state_detection_mode

        # standard dark state is the |0> state
        if mode == 'Standard':
            self.addSequence(DopplerCooling)
            self.addSequence(OpticalPumping)
            if self.parameters.BrightStatePumping.start_with_Hadamard == 'On':
                self.addSequence(BrightStatePumping)
            self.addSequence(StandardStateDetection)

        # shelving dark state is the |1> state
        elif mode == 'Shelving':
            self.addSequence(TurnOffAll)
            self.addSequence(ShelvingDopplerCooling)
            self.addSequence(BrightStatePumping)
            self.addSequence(Shelving)
            self.addSequence(ShelvingStateDetection)
            self.addSequence(Deshelving)
