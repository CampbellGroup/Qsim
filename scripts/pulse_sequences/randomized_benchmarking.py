from sub_sequences.shelving import Shelving
from sub_sequences.deshelving import Deshelving
from sub_sequences.turn_off_all import TurnOffAll
from sub_sequences.optical_pumping import OpticalPumping
from sub_sequences.doppler_cooling import DopplerCooling
from sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from sub_sequences.randomized_benchmarking import RandomizedBenchmarkingPulse
from sub_sequences.microwave_pulse_sequences.MicrowaveSequenceStandard import MicrowaveSequenceStandard
from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence


class RandomizedBenchmarking(pulse_sequence):

    required_subsequences = [DopplerCooling, StandardStateDetection,
                             ShelvingStateDetection, TurnOffAll,
                             ShelvingDopplerCooling, Shelving, Deshelving,
                             OpticalPumping, RandomizedBenchmarkingPulse,
                             MicrowaveSequenceStandard]
    required_parameters = [
        ('Modes', 'state_detection_mode'),
    ]

    def sequence(self):
        mode = self.parameters.Modes.state_detection_mode

        # standard bright state is the 1 state
        if mode == 'Standard':
            self.addSequence(TurnOffAll)
            self.addSequence(DopplerCooling)
            self.addSequence(OpticalPumping)
            self.addSequence(RandomizedBenchmarkingPulse)
            self.addSequence(StandardStateDetection)

        # shelving bright state is the 0 state
        elif mode == 'Shelving':
            self.addSequence(TurnOffAll)
            self.addSequence(ShelvingDopplerCooling)
            self.addSequence(OpticalPumping)
            self.addSequence(RandomizedBenchmarkingPulse)
            self.addSequence(Shelving)
            self.addSequence(ShelvingStateDetection)
            self.addSequence(Deshelving)
