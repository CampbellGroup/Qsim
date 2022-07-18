from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.state_detection.shelving_state_detection import shelving_state_detection
from sub_sequences.shelving_doppler_cooling import shelving_doppler_cooling
from Qsim.scripts.pulse_sequences.BrightStatePumping import bright_state_pumping
from sub_sequences.empty_sequence import empty_sequence
from sub_sequences.shelving import shelving
from sub_sequences.deshelving import deshelving
from sub_sequences.turn_off_all import turn_off_all


class shelving_point(pulse_sequence):

    required_subsequences = [turn_off_all, shelving_doppler_cooling, shelving,
                             deshelving, shelving_state_detection, empty_sequence, bright_state_pumping]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)

        self.addSequence(turn_off_all)
        self.addSequence(bright_state_pumping)

        self.addSequence(turn_off_all)
        self.addSequence(shelving)

        self.addSequence(turn_off_all)
        self.addSequence(empty_sequence)

        self.addSequence(turn_off_all)
        self.addSequence(shelving_state_detection)

        self.addSequence(turn_off_all)
        self.addSequence(deshelving)
