from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.Shelving import shelving
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.MicrowaveInterrogation import microwave_interrogation
from sub_sequences.Deshelving import deshelving


class shelving_dark_spam(pulse_sequence):

    required_subsequences = [shelving, shelving_doppler_cooling, shelving_state_detection, deshelving,
                             optical_pumping, microwave_interrogation]

    required_parameters = [
                           ]

    def sequence(self):
        self.addSequence(shelving_doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(microwave_interrogation)
        self.addSequence(shelving)
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelving)
