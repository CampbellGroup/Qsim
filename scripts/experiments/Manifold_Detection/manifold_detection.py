import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.pulse_sequences.sub_sequences.ManifoldStateDetection import manifold_state_detection as sequence
from labrad.units import WithUnit as U
import time
import numpy as np


class off_resonant_shelving_measurement(QsimExperiment):

    name = 'Manifold Detection'

    exp_parameters = [
        ('ddsDefaults', 'repump_760_1_power'),
        ('ddsDefaults', 'repump_760_2_power'),
        ('ddsDefaults', 'DP411_power')
    ]

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.pulser = cxn.pulser
        self.pmt = cxn.normalpmtflow
        self.pzt_server = cxn.piezo_server

    def run(self, cxn, context):

        self.setup_datavault('event_num', 'wait_time') #TODO: update this

        self.program_pulser(sequence)

        still_there = True
        while still_there:
            init_time = time.time()

            should_break = self.update_progress(np.random.random())
            if should_break:
                break

            # check that the ion is still there
            still_there = self.rescue_ion(5.0)

            # try to shelve an ion until it works
            is_shelved = False
            while is_shelved is False:
                is_shelved = self.attempt_shelving

            # set the brightness threshold
            self.fluorescence, counts = self.get_average_counts()
            print('initial fluorescence is {} counts'.format(self.fluorescence))
            self.current_fluorescence = self.fluorescence

            # run for 5 minutes or until fluorescence leaves acceptable range, binning the data and outputting it to datavault
            while (time.time() - init_time < 300) or abs(self.current_fluorescence - self.fluorescence) < self.p.manifoldDetection.cavity_threshold
                should_break = self.update_progress(np.random.random())
                if should_break:
                    break
                self.current_fluorescence, counts = self.get_average_counts()
                hist = self.process_data(counts)
                self.plot_hist(hist, folder_name='ManifoldDetection')

            # move fluorescence back to middle of range
            self.correct_cavity_drift() #TODO: define this function

    def get_average_counts(self):
        counts = self.run_sequence(max_runs=1000, num=1)
        avg = np.mean(counts)
        return avg, counts

    def correct_cavity_drift(self):
        delta = self.current_fluorescence - self.fluorescence
        j = 0
        while np.abs(delta) > self.p.manifoldDetection.cavity_threshold:
            if j > 10:
                return False
            # take advantage of the fact that +voltage=red, -voltage=blue if we're red of the line
            new_cavity_voltage = self.cavity_voltage + 0.01 * np.sign(delta)
            print('Moving cavity from {} V to {} V'.format(self.cavity_voltage, new_cavity_voltage))
            self.pzt_server.set_voltage(self.cavity_chan, U(new_cavity_voltage, 'V'))
            self.cavity_voltage = new_cavity_voltage
            self.current_fluorescence, counts = self.get_average_counts()
            delta = self.current_fluorescence - self.fluorescence
        return True

    def attempt_shelving(self):
        self.toggle_repump_lasers('Off')
        before_counts = np.mean(self.pmt.get_next_counts('ON', True))
        self.toggle_shelving_laser('On')
        time.sleep(self.p.manifoldDetection.shelving_attempt_time) #TODO: add this to the parameter vault
        self.toggle_shelving_laser('Off')
        after_counts = np.mean(self.pmt.get_next_counts('ON', True))
        if after_counts < before_counts * 0.6:
            return True
        return False

    def rescue_ion(self, threshold):
        self.toggle_repump_lasers('On')
        self.toggle_shelving_laser('Off')
        time.sleep(self.p.manifoldDetection.rescue_time) #should default to 10 seconds
        counts = self.pmt.get_next_counts('ON', True)
        if counts > threshold:
            return True
        else:
            return False

    def toggle_repump_lasers(self, state):
        if state == 'Off':
            self.pulser.amplitude('760SP', U(-46.0, 'dBm'))
            self.pulser.amplitude('760SP2', U(-46.0, 'dBm'))
        if state == 'On':
            self.pulser.amplitude('760SP', self.p.ddsDefaults.repump_760_1_power)
            self.pulser.amplitude('760SP2', self.p.ddsDefaults.repump_760_2_power)

    def toggle_shelving_laser(self, state):
        if state == 'Off':
            self.pulser.amplitude('411DP', U(-46.0, 'dBm'))
        if state == 'On':
            self.pulser.amplitude('411DP', self.p.ddsDefaults.DP411_power)

    def finalize(self, cxn, context):
        self.toggle_repump_lasers('On')
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = off_resonant_shelving_measurement(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
