from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import shelving_doppler_cooling
from scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import shelving_state_detection
from scripts.pulse_sequences.sub_sequences.deshelving import deshelving
from scripts.pulse_sequences.sub_sequences.turn_off_all import turn_off_all
from sub_sequences.BrightStatePumping import bright_state_pumping
from scripts.pulse_sequences.sub_sequences.shelving import shelving


class manifold_measurement(pulse_sequence):

    required_subsequences = [shelving_doppler_cooling, shelving_state_detection,
                             turn_off_all, bright_state_pumping, shelving, deshelving]

    required_parameters = [
                           ('BrightStatePumping', 'bright_prep_method')
                           ]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)

        self.addSequence(turn_off_all)
        self.addSequence(bright_state_pumping)

        self.addSequence(turn_off_all)
        self.addSequence(shelving_state_detection)

        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)

        self.addSequence(turn_off_all)
        self.addSequence(shelving)

        self.addSequence(turn_off_all)
        self.addSequence(shelving_state_detection)

        self.addSequence(turn_off_all)
        self.addSequence(deshelving)
