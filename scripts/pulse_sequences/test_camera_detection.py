from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.test_camera_detection import TestCameraDetection


class TestCameraDetection(pulse_sequence):
    required_subsequences = [TestCameraDetection]

    def sequence(self):
        self.addSequence(TestCameraDetection)
