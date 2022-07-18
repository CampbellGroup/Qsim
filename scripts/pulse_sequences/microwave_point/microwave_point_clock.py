from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.doppler_cooling import DopplerCooling
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.microwave_interrogation_clock import MicrowaveInterrogationClock
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping


class MicrowavePointClock(pulse_sequence):

    required_subsequences = [TurnOffAll, DopplerCooling,
                             MicrowaveInterrogationClock,
                             StandardStateDetection,
                             OpticalPumping]

    required_parameters = [
        ]

    def sequence(self):
        p = self.parameters

        self.addSequence(TurnOffAll)
        self.addSequence(DopplerCooling)
        self.addSequence(OpticalPumping)
        self.addSequence(MicrowaveInterrogationClock)
        self.addSequence(StandardStateDetection)
