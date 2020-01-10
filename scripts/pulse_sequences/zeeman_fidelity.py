from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.QuadrupoleInterogation import quadrupole_interogation
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.ZeemanOpticalPumping import zeeman_bright_optical_pumping
from sub_sequences.ZeemanOpticalPumping import zeeman_dark_optical_pumping
from sub_sequences.Shelving import shelving
from sub_sequences.Deshelving import deshelving


class zeeman_fidelity(pulse_sequence):

    required_subsequences = [turn_off_all, quadrupole_interogation, shelving_state_detection,
                             shelving, shelving_doppler_cooling, deshelving,
                             zeeman_bright_optical_pumping, zeeman_dark_optical_pumping]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)
        self.addSequence(zeeman_bright_optical_pumping)
        self.addSequence(shelving)
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelving)

        self.addSequence(shelving_doppler_cooling)
        self.addSequence(zeeman_dark_optical_pumping)
        self.addSequence(shelving)
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelving)
