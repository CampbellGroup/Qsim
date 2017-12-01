import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time
import numpy as np

__scriptscanner_name__ = 'MLpiezoscan' # this should match the class name
class MLpiezoscan(QsimExperiment):

    name = 'ML Piezo Scan'

    exp_parameters = []
    exp_parameters.append(('MLpiezoscan', 'scan'))
    exp_parameters.append(('MLpiezoscan', 'average'))
    exp_parameters.append(('MLpiezoscan', 'mode'))
    exp_parameters.append(('MLpiezoscan', 'detuning'))
    exp_parameters.append(('MLpiezoscan', 'power'))
    exp_parameters.append(('MLpiezoscan', 'take_images'))
    exp_parameters.append(('MLpiezoscan', 'number_of_images'))

    exp_parameters.append(('Transitions', 'main_cooling_369'))

    exp_parameters.append(('images', 'image_center_x'))
    exp_parameters.append(('images', 'image_center_y'))
    exp_parameters.append(('images', 'image_width'))
    exp_parameters.append(('images', 'image_height'))

    def initialize(self, cxn, context, ident):

        self.ident = ident

        self.TTL = cxn.arduinottl

        self.chan = 1
        self.keithley = self.cxn.keithley_2230g_server
        self.keithley.select_device(0)

        self.pmt = self.cxn.normalpmtflow
        self.init_mode = self.pmt.getcurrentmode()
        self.pulser = cxn.pulser
        self.init_freq = self.pulser.frequency('369DP')
        self.init_power = self.pulser.amplitude('369DP')

    def run(self, cxn, context):

        '''
        Main loop
        '''
        self.set_scannable_parameters()
        if self.p.MLpiezoscan.take_images:
            self.cam = cxn.andor_server
            self.init_camera()
        self.keithley.gpib_write('APPLy CH1,' + str(self.init_volt) + 'V')
        self.keithley.output(self.chan, True)
        time.sleep(0.5) # allow voltage to settle
        self.pulser.frequency('369DP',self.WLcenter + self.detuning/2.0) # this is real laser detuning
        self.pulser.amplitude('369DP', self.power)
        cxn.arduinottl.ttl_output(12, True)
        self.path = self.setup_datavault('Volts', 'kcounts/sec')
        self.setup_grapher('ML Piezo Scan')
        try:
            MLfreq = cxn.bristol_521.get_wavelength()
            self.dv.add_parameter('Bristol Reading', MLfreq)
        except:
            pass

        if self.mode == 'DIFF':
            self.pmt.set_mode('Differential')
        else:
            self.pmt.set_mode('Normal')

        image_data = np.array([])
        for i, volt in enumerate(self.x_values):
            if ((self.p.MLpiezoscan.take_images) and (i % self.image_interval == 0)):
                self.pmt.set_mode('Normal')
                cxn.arduinottl.ttl_output(8, True)
                cxn.arduinottl.ttl_output(8, False)
                time.sleep(1)
                new_image = self.cam.get_most_recent_image()
                self.grapher.plot_image(new_image, self.data_size, 'Images',
                                        self.path[1] + ' ' + str(i + 1) + ' Voltage = ' + str(volt))
                cxn.arduinottl.ttl_output(8, True)
                cxn.arduinottl.ttl_output(8, False)
                time.sleep(1)
                if self.mode == 'DIFF':
                    self.pmt.set_mode('Differential')
                else:
                    self.pmt.set_mode('Normal')
                image_data = np.concatenate([image_data, new_image])
            should_break = self.update_progress(i/float(len(self.x_values)))
            self.keithley.gpib_write('APPLy CH1,' + str(volt) + 'V')  # we write direct GPIB for speed
            counts = self.pmt.get_next_counts(self.mode, self.average, True)
            self.dv.add(volt, counts)
            if should_break:
                break
        if self.p.MLpiezoscan.take_images:
            self.save_camera_data(image_data)

    def set_scannable_parameters(self):
        '''
        gets parameters, called in run so scan works
        '''

        self.power = self.p.MLpiezoscan.power
        self.WLcenter = self.p.Transitions.main_cooling_369
        self.detuning = self.p.MLpiezoscan.detuning
        self.mode = self.p.MLpiezoscan.mode
        self.average = int(self.p.MLpiezoscan.average)
        self.x_values = self.get_scan_list(self.p.MLpiezoscan.scan, 'V')
        self.init_volt = self.x_values[0]

    def init_camera(self):
        self.num_images = self.p.MLpiezoscan.number_of_images
        self.image_interval = int(len(self.x_values) / self.num_images)
        center_y = self.p.images.image_center_x['pix'] #  switched for same reason
        center_x = self.p.images.image_center_y['pix']
        height = self.p.images.image_width['pix']
        width = self.p.images.image_height['pix']  # switched due to transpose of camera data
        self.exposure = self.cam.get_exposure_time()
        self.x_pixel_range = [int(center_x - width/2), int(center_x + width/2)] # rounds image size
        self.y_pixel_range = [int(center_y - height/2), int(center_y + height/2)]
        self.image_x_length = self.x_pixel_range[-1] - self.x_pixel_range[0] + 1
        self.image_y_length = self.y_pixel_range[-1] - self.y_pixel_range[0] + 1
        self.data_size = [self.image_x_length, self.image_y_length]

        self.cam.abort_acquisition()
        self.cam.set_image_region([1, 1, self.y_pixel_range[0], self.y_pixel_range[1], self.x_pixel_range[0], self.x_pixel_range[1]])
        self.cam.start_live_display()

    def save_camera_data(self, image_data):
        num_images_final = len(image_data)/(self.data_size[0]*self.data_size[1])
        self.dv.save_image(image_data, self.data_size, int(num_images_final), self.path[1])

    def finalize(self, cxn, context):
        if self.p.MLpiezoscan.take_images:
            hor_max, ver_max =  self.cam.get_detector_dimensions(None)
            hor_min, ver_min = [1, 1]
            self.cam.abort_acquisition()
            self.cam.set_image_region([1, 1, hor_min, hor_max, ver_min, ver_max])
            self.cam.start_live_display()
        self.keithley.gpib_write('APPLy CH1,' + str(self.x_values[0]) + 'V')
        self.pulser.frequency('369DP', self.init_freq)
        self.pulser.amplitude('369DP', self.init_power)
        cxn.arduinottl.ttl_output(12, False)
        self.pmt.set_mode(self.init_mode)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MLpiezoscan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
