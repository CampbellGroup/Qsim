import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit
import time
import numpy as np
from scipy.ndimage.interpolation import rotate

class velocity_class(QsimExperiment):

    name = 'velocity_class'

    exp_parameters = []

    exp_parameters.append(('images', 'image_center_x'))
    exp_parameters.append(('images', 'image_center_y'))
    exp_parameters.append(('images', 'image_width'))
    exp_parameters.append(('images', 'image_height'))
    exp_parameters.append(('images', 'rotation_angle'))
    exp_parameters.append(('images', 'number_images'))

    exp_parameters.append(('velocity_class', 'CW_cooling_power'))
    exp_parameters.append(('velocity_class', 'CW_cooling_time'))
    exp_parameters.append(('velocity_class', 'ML_piezo_voltage'))
    exp_parameters.append(('velocity_class', 'tickle_freq'))
    exp_parameters.append(('velocity_class', 'tickle_time'))
    exp_parameters.append(('velocity_class', 'tickle_off_time'))
    exp_parameters.append(('velocity_class', 'tickle_amplitude'))
    exp_parameters.append(('velocity_class', 'ML_precooling_time'))
    exp_parameters.append(('velocity_class', 'background_subtraction'))

    exp_parameters.append(('Transitions', 'main_cooling_369'))

    def initialize(self, cxn, context, ident):

        self.ident = ident

        self.TTL = cxn.arduinottl
        self.pmt = cxn.normalpmtflow
        self.pulser = cxn.pulser
        self.keithley = cxn.keithley_2230g_server
        self.rg = self.cxn.dg1022_rigol_server
        self.cam = cxn.andor_server

        self.save_ctx = self.dv.context()

        self.rg_chan = 1
        self.kt_chan = 1

        self.keithley.select_device(0)

        self.init_mode = self.pmt.getcurrentmode()
        self.init_freq = self.pulser.frequency('369DP')
        self.init_power = self.pulser.amplitude('369DP')

    def run(self, cxn, context):

        self.path = self.setup_datavault('Amplitude', 'Velocity')
        #self.setup_grapher('velocity_class')
        #self.x_values = self.get_scan_list(self.p.velocity_class.tickle_amplitudes, units='V')
        self.set_scannable_parameters()
        self.get_initial_settings()
        self.set_exp_settings()


        #for i, x_point inamplitudes enumerate(self.x_values):
        image_data = np.array([])

        # Doppler cool
        self.pulser.amplitude('369DP', self.cw_cooling_power)
        time.sleep(self.cw_cooling_time['s'])

        # CW off ML on
        self.pulser.amplitude('369DP', WithUnit(-46.0, 'dBm'))
        self.TTL.ttl_output(12, True)
        time.sleep(self.ML_precooling_time['s'])
        image = self.take_image('pre-tickle')
        image_data = np.concatenate([image_data, image])

        # Tickle on
        self.rg.applywaveform('sine', self.tickle_freq,
                                  self.tickle_amplitude, WithUnit(0.0, 'V'), self.rg_chan)
        time.sleep(0.1)
        self.rg.set_output(self.rg_chan, True)
        time.sleep(self.tickle_time['s'])

        # Take tickled image
        #image = self.take_image('during tickle', i)
        #image_data = np.concatenate([image_data, image])

        # Tickle Off and take ML only image
        self.rg.set_output(self.rg_chan, False)
        time.sleep(self.tickle_off_time['s'])

        image_num = 0
        while image_num < self.number_images:
            image = self.take_image('after tickle' + ' ' + str(image_num))
            image_data = np.concatenate([image_data, image])
            if image_num == 0:
                column_sum = self.analyze(image)
                sum_image = image
            else:
                column_sum += self.analyze(image)
                sum_image += image
            should_break = self.update_progress(image_num/float(self.number_images))
            if should_break:
                break
            image_num += 1

        self.process_data(column_sum/float(self.number_images))

        # ML off
        self.TTL.ttl_output(12, False)
        avg_image = sum_image/float(self.number_images)
        self.save_camera_data(avg_image.astype(int))


    def process_data(self, column_sum):

        self.dv.cd(self.path[0], context=self.save_ctx)
        self.dv.cd(self.path[1], True, context=self.save_ctx)
        dataset = self.dv.new('stacked_images' + ' - ' + str(self.path[1]), [('frequency', 'MHz')],
                              [('', 'Intensity', 'A.U.')], context=self.save_ctx)
        self.dv.add(column_sum, context=self.save_ctx)
        self.grapher.plot(dataset, 'velocity_class', False)

    def analyze(self, image):
        x_array = np.array(range(self.image_x_length)) / 8.0
        x_array = (x_array - x_array[-1]/2.0)#* 2 * np.pi * self.tickle_freq['MHz'] / (369.5e-9)
        image = image.reshape((self.image_x_length, self.image_y_length))
        window = 25
        lower_window = int(self.image_y_length/2.0 - window/2.0)
        upper_window = int(self.image_y_length/2.0 + window / 2.0)
        image = image[:,lower_window:upper_window]
        summed = np.sum(image, 1)
        summed -= np.min(summed)
        data = np.array(np.vstack((x_array, summed)).transpose(), dtype='float')
        return data

    def take_image(self, name):
        time.sleep(self.exposure['s']*2)
        row_image = self.cam.get_most_recent_image()
        new_image = row_image.reshape(self.image_x_length, self.image_y_length)
        if self.background_subtraction == True:
            new_image -= self.bg_image
        rotated_image = rotate(new_image, self.image_rotation_angle['deg'], reshape=False)
        rotated_row_image = rotated_image.reshape(-1)
        self.grapher.plot_image(rotated_row_image, self.data_size, 'Images',
                                self.path[1] + ' ' + name)
        return rotated_row_image

    def save_camera_data(self, image_data):
        self.dv.cd(self.path[0], context = self.save_ctx)
        self.dv.cd(self.path[1], True, context = self.save_ctx)
        self.dv.save_image(image_data, self.data_size, 1, self.path[1], context = self.save_ctx)

    def set_exp_settings(self):

        self.cam.abort_acquisition()
        self.cam.set_image_region(
            [1, 1, self.y_pixel_range[0], self.y_pixel_range[1], self.x_pixel_range[0], self.x_pixel_range[1]])
        self.cam.start_live_display()

        if self.background_subtraction == True:
            repump_amp = self.pulser.amplitude('935SP')
            cw_amp = self.pulser.amplitude('369DP')
            self.pulser.amplitude('935SP', WithUnit(-46.0, 'dBm'))
            self.TTL.ttl_output(12, True)
            self.pulser.amplitude('369DP', WithUnit(-46.0, 'dBm'))
            time.sleep(1.0)
            self.background_subtraction = False
            self.bg_image = self.take_image('background_subtraction')
            self.TTL.ttl_output(12, False)
            self.pulser.amplitude('935SP', repump_amp)
            self.pulser.amplitude('369DP', cw_amp)
            self.background_subtraction = True
            self.bg_image = self.bg_image.reshape(self.image_x_length, self.image_y_length)

        self.keithley.gpib_write('APPLy CH1,' + str(self.ML_piezo_voltage['V']) + 'V')
        self.keithley.output(self.kt_chan, True)

        self.pulser.frequency('369DP',self.WLcenter - WithUnit(10.0, 'MHz')/2.0) # this is real laser detuning

    def get_initial_settings(self):

        self.init_mode = self.pmt.getcurrentmode()
        self.init_freq = self.pulser.frequency('369DP')
        self.init_power = self.pulser.amplitude('369DP')
        self.exposure = self.cam.get_exposure_time()

    def set_scannable_parameters(self):
        center_y = self.p.images.image_center_x['pix'] #  switched for same reason
        center_x = self.p.images.image_center_y['pix']
        height = self.p.images.image_width['pix']
        width = self.p.images.image_height['pix']  # switched due to transpose of camera data
        self.number_images = self.p.images.number_images
        self.image_rotation_angle = self.p.images.rotation_angle
        self.x_pixel_range = [int(center_x - width/2), int(center_x + width/2)] # rounds image size
        self.y_pixel_range = [int(center_y - height/2), int(center_y + height/2)]
        self.image_x_length = self.x_pixel_range[-1] - self.x_pixel_range[0] + 1
        self.image_y_length = self.y_pixel_range[-1] - self.y_pixel_range[0] + 1
        self.data_size = [self.image_x_length, self.image_y_length]
        self.WLcenter = self.p.Transitions.main_cooling_369
        self.cw_cooling_power = self.p.velocity_class.CW_cooling_power
        self.cw_cooling_time = self.p.velocity_class.CW_cooling_time
        self.ML_piezo_voltage = self.p.velocity_class.ML_piezo_voltage
        self.tickle_freq = self.p.velocity_class.tickle_freq
        self.tickle_time = self.p.velocity_class.tickle_time
        self.tickle_off_time = self.p.velocity_class.tickle_off_time
        self.tickle_amplitude = self.p.velocity_class.tickle_amplitude
        self.ML_precooling_time = self.p.velocity_class.ML_precooling_time
        self.background_subtraction = self.p.velocity_class.background_subtraction


    def finalize(self, cxn, context):
        hor_max, ver_max = self.cam.get_detector_dimensions(None)
        hor_min, ver_min = [1, 1]
        self.cam.abort_acquisition()
        self.cam.set_image_region([1, 1, hor_min, hor_max, ver_min, ver_max])
        self.cam.start_live_display()
        self.pulser.frequency('369DP', self.init_freq)
        self.pulser.amplitude('369DP', self.init_power)
        cxn.arduinottl.ttl_output(12, False)
        self.pmt.set_mode(self.init_mode)
        self.rg.set_output(self.rg_chan, False)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = velocity_class(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
