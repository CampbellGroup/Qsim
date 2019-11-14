from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.BrightStatePumping import bright_state_pumping
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.QuadrupoleInterogation import quadrupole_interogation
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.Shelving import shelving
from labrad.units import WithUnit as U


class quadrupole_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling,
                             quadrupole_interogation, shelving_state_detection,
                             optical_pumping, shelving, shelving_doppler_cooling, bright_state_pumping]

    required_parameters = [
        ]

    def sequence(self):

        self.end = U(10.0, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(bright_state_pumping)
        self.addSequence(quadrupole_interogation)
        self.addSequence(shelving_state_detection)
