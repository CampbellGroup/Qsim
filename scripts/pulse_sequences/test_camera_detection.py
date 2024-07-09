from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.test_camera_detection import TestCameraDetection


class TestCameraDetection(PulseSequence):
    required_subsequences = [TestCameraDetection]

    def sequence(self):
        self.add_sequence(TestCameraDetection)
