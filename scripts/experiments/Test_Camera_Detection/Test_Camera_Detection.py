import labrad
from Qsim.scripts.pulse_sequences.test_camera_detection import test_camera_detection as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np

class TestCameraDetection(QsimExperiment):
    """
    test experiment to get EMCCD camera detection working
    """

    name = 'Test Camera Detection'

    exp_parameters = []
    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.context = context
        self.cam = cxn.andor_server
        

    def run(self, cxn, context):
        # number of images to acquire and show on the GUI
        n = 1

        i = 0
        while i < n:
            should_break = self.update_progress(np.random.rand())
            if should_break:
                break

            self.program_pulser(sequence)
            self.run_test_sequence()
            i += 1

    def run_test_sequence(self):
        self.pulser.start_number(1)
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()

    def setup_camera(self, cam):
        cam.abort_acquisition()
        init_trigger_mode = cam.get_trigger_mode()
        if init_trigger_mode != 'External':
            cam.set_trigger_mode('External')



if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = TestCameraDetection(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
