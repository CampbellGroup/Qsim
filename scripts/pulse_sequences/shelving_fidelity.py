from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.Shelving import shelving
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from Qsim.scripts.pulse_sequences.BrightStatePumping import bright_state_pumping
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.Deshelving import deshelving


class shelving_fidelity(pulse_sequence):

    required_subsequences = [shelving, shelving_doppler_cooling, shelving_state_detection, deshelving,
                             turn_off_all, bright_state_pumping, optical_pumping]

    required_parameters = [
                           ]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)

        self.addSequence(turn_off_all)
        self.addSequence(bright_state_pumping)

        self.addSequence(turn_off_all)
        self.addSequence(shelving)

        self.addSequence(turn_off_all)
        self.addSequence(shelving_state_detection)

        self.addSequence(turn_off_all)
        self.addSequence(deshelving)

        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)

        self.addSequence(turn_off_all)
        self.addSequence(optical_pumping)

        self.addSequence(turn_off_all)
        self.addSequence(shelving)

        self.addSequence(turn_off_all)
        self.addSequence(shelving_state_detection)

        self.addSequence(turn_off_all)
        self.addSequence(deshelving)
