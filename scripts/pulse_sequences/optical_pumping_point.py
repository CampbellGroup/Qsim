from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import doppler_cooling
from sub_sequences.turn_off_all import turn_off_all
from sub_sequences.optical_pumping import optical_pumping
from sub_sequences.doppler_cooling_fiber_eom import doppler_cooling_fiber_eom
from sub_sequences.state_detection.standard_state_detection_fiber_eom import standard_state_detection_fiber_eom
from sub_sequences.state_detection.standard_state_detection import standard_state_detection
from sub_sequences.state_detection.shelving_state_detection import shelving_state_detection
from sub_sequences.deshelving import deshelving
from sub_sequences.shelving import shelving


class optical_pumping_point(pulse_sequence):

    required_subsequences = [doppler_cooling, standard_state_detection, turn_off_all
                             , optical_pumping, doppler_cooling, shelving_state_detection,
                             deshelving, shelving, doppler_cooling_fiber_eom,
                             standard_state_detection_fiber_eom]

    required_parameters = [
        ('OpticalPumping', 'method'),
        ('Modes', 'state_detection_mode')
                           ]

    def sequence(self):
        p = self.parameters

        self.addSequence(turn_off_all)

        if p.OpticalPumping.method == 'Standard':
            self.addSequence(doppler_cooling)
            self.addSequence(optical_pumping)
            self.addSequence(standard_state_detection)

        elif p.OpticalPumping.method == "StandardFiberEOM":
            self.addSequence(doppler_cooling_fiber_eom)
            self.addSequence(optical_pumping)
            self.addSequence(standard_state_detection_fiber_eom)

        elif p.OpticalPumping.method == 'QuadrupoleOnly':
            if p.Modes.state_detection_mode == 'Shelving':
                self.addSequence(doppler_cooling)
                self.addSequence(optical_pumping)
                self.addSequence(shelving)
                self.addSequence(shelving_state_detection)
                self.addSequence(deshelving)
            if p.Modes.state_detection_mode == 'Standard':
                self.addSequence(doppler_cooling)
                self.addSequence(optical_pumping)
                self.addSequence(standard_state_detection)
                self.addSequence(deshelving)