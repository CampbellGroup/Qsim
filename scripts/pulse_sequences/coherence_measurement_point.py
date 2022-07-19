from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import DopplerCooling
from sub_sequences.turn_off_all import TurnOffAll
from sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from sub_sequences.optical_pumping import OpticalPumping
from sub_sequences.empty_sequence import EmptySequence
from sub_sequences.shelving import Shelving
from sub_sequences.deshelving import Deshelving
from sub_sequences.coherence_measurement_microwave_sequence import CoherenceMeasurementMicrowaveSequence


class CoherenceMeasurementPoint(pulse_sequence):

    required_subsequences = [TurnOffAll, DopplerCooling,
                             ShelvingStateDetection,
                             Deshelving, StandardStateDetection,
                             OpticalPumping, EmptySequence, Shelving,
                             CoherenceMeasurementMicrowaveSequence, ShelvingDopplerCooling]

    required_parameters = [
                          ('Modes', 'state_detection_mode')
        ]

    def sequence(self):
        mode = self.parameters.Modes.state_detection_mode

        if mode == 'Shelving':
            self.addSequence(TurnOffAll)
            self.addSequence(ShelvingDopplerCooling)
            self.addSequence(OpticalPumping)
            self.addSequence(CoherenceMeasurementMicrowaveSequence)
            self.addSequence(Shelving)
            self.addSequence(ShelvingStateDetection)
            self.addSequence(Deshelving)
        elif mode == 'Standard':
            self.addSequence(TurnOffAll)
            self.addSequence(DopplerCooling)
            self.addSequence(OpticalPumping)
            self.addSequence(CoherenceMeasurementMicrowaveSequence)
            self.addSequence(StandardStateDetection)
