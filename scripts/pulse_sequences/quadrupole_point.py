from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.BrightStatePumping import bright_state_pumping
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.QuadrupoleInterrogation import quadrupole_interrogation
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.Deshelving import deshelving
from labrad.units import WithUnit as U


class quadrupole_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling,
                             quadrupole_interrogation, shelving_state_detection, deshelving,
                             optical_pumping, bright_state_pumping]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(bright_state_pumping)
        self.addSequence(quadrupole_interrogation)
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelving)
