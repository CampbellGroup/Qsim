from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.microwave_interrogation.microwave_interrogation import microwave_interrogation
from sub_sequences.doppler_cooling import doppler_cooling
from sub_sequences.quadrupole_interrogation import quadrupole_interrogation
from sub_sequences.turn_off_all import turn_off_all
from sub_sequences.state_detection.standard_state_detection import standard_state_detection
from sub_sequences.optical_pumping import optical_pumping
from sub_sequences.deshelving import deshelving


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
