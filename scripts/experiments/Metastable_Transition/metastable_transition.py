import labrad
import numpy as np
import time
import os
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment


class metastable_transition(QsimExperiment):

    name = 'Meta-Stable Transition'

    exp_parameters = []
    exp_parameters.append(('metastable', 'M2_scan'))
    exp_parameters.append(('metastable', 'pause_time'))
    dv_path = "/home/qsimexpcontrol/LabRAD/data"

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.path = self.setup_datavault('Multipole', 'Image number')
        self.dv.cd(self.path[1], True) # creates a folder for the images
        self.dv.new('frame_info', [('frame_number', 'num')], [('multipole', '', 'num')])
        self.mps = cxn.multipole_server
        self.init_multipoles = cxn.multipole_server.get_multipoles()
        self.cam = cxn.andor_server
        self.grapher = cxn.grapher
        self.init_camera()

    def run(self, cxn, context):
        self.x_values = self.get_scan_list(self.p.metastable.M2_scan, units=None)
        multipoles = np.array(self.init_multipoles)
        image_data = np.array([])
        for i, setting in enumerate(self.x_values):
            should_break = self.update_progress(i/float(len(self.x_values)))
            if should_break:
                break
            new_image = self.cam.get_most_recent_image()
            self.grapher.plot_image(new_image, self.data_size, 'Images',
                                    self.path[1] + ' ' + str(i + 1) + ' Multipole = ' + str(setting))
            image_data = np.concatenate([image_data, new_image])
            multipoles[4] = setting
            self.mps.set_multipoles(multipoles)
            self.dv.add(i + 1, setting)
            time.sleep(self.p.metastable.pause_time['s'])
        self.saveData(image_data)

    def saveData(self, image_data):
        try:
            self.dv.save_image(image_data, self.data_size, len(self.x_values))
        except:
            pass

    def init_camera(self):
        self.image_region = self.cam.get_image_region()
        self.x_bin = self.image_region[0]
        self.y_bin = self.image_region[1]
        self.x_pixel_range = [self.image_region[2], self.image_region[3]]
        self.y_pixel_range = [self.image_region[4], self.image_region[5]]
        self.image_x_length = self.x_pixel_range[-1] - self.x_pixel_range[0] + 1
        self.image_y_length = self.y_pixel_range[-1] - self.y_pixel_range[0] + 1
        self.data_size = [self.image_x_length, self.image_y_length]
        self.dv.add_parameter('image size', self.data_size)
        self.dv.add_parameter('binning', [self.x_bin, self.y_bin])

    def finalize(self, cxn, context):
        self.mps.set_multipoles(self.init_multipoles)

if __name__ == '__main__':
    #normal way to launch
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = metastable_transition(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
