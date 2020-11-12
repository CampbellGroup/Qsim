from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.MicrowaveInterrogation import microwave_interrogation
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.QuadrupoleInterrogation import quadrupole_interrogation
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.Deshelving import deshelving


class quadrupole_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling, quadrupole_interrogation,
                             deshelving, optical_pumping, microwave_interrogation,
                             standard_state_detection]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(microwave_interrogation)
        self.addSequence(quadrupole_interrogation)
        self.addSequence(standard_state_detection)
        self.addSequence(deshelving)
