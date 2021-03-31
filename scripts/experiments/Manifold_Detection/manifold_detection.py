import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
# from Qsim.scripts.pulse_sequences.sub_sequences.ManifoldStateDetection import manifold_state_detection as sequence
from labrad.units import WithUnit as U
import time
import numpy as np


class manifold_detection(QsimExperiment):

    name = 'Manifold Detection'

    exp_parameters = [
        ('ddsDefaults', 'repump_760_1_power'),
        ('ddsDefaults', 'repump_760_2_power'),
    ]

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.pulser = cxn.pulser
        self.pmt = cxn.normalpmtflow
        self.pzt_server = cxn.piezo_server
        self.cavity_chan = 1
        self.cavity_voltage = self.pzt_server.get_voltage(self.cavity_chan)
        self.cavity_rails = (self.cavity_voltage-1, self.cavity_voltage+1)

    def run(self, cxn, context):
        ion_dead = False

        self.setup_datavault()

        self.pmt.set_time_length(U(10, "ms"))

        still_there = True
        while still_there:
            for isdark in [True, False]:
                init_time = time.time()

                should_break = self.update_progress(0.01)
                if should_break: break

                self.fluorescence, counts = self.get_average_counts(100)
                print('initial fluorescence is {} counts'.format(self.fluorescence))

                print('isdark: {}'.format(isdark))
                if isdark:
                    # try to shelve an ion until it works
                    is_shelved = False
                    while is_shelved is False:
                        should_break = self.update_progress((time.time() - init_time) / 300.0)
                        if should_break: break
                        is_shelved = self.attempt_shelving()

                # set the brightness threshold

                self.current_fluorescence, counts = self.get_average_counts(10)
                print("pre-loop fluorescence is {}".format(self.current_fluorescence))
                if self.current_fluorescence < 5.0:
                    print('Current fluorescence too low. Attempting to rescue ion')
                    if not self.rescue_ion(5.0):
                        ion_dead = True
                        break
                else:

                    # run for 5 minutes or until fluorescence leaves acceptable range, binning the data and outputting it to datavault
                    while time.time() - init_time < 300:  # or abs(self.current_fluorescence - self.fluorescence) < 1.0:
                        if self.current_fluorescence < 5.0:
                            print('Current fluorescence too low. Attempting to rescue ion')
                            if not self.rescue_ion(5.0):
                                ion_dead = True
                                break
                        should_break = self.update_progress((time.time()-init_time)/300.0)
                        if should_break: break
                        self.current_fluorescence, counts = self.get_average_counts()
                        print("   current fluorescence is {}".format(self.current_fluorescence))
                        if isdark:
                            self.dv.add(np.column_stack((np.arange(len(counts)), np.array(counts))),
                                        context=self.dark_counts_context)
                        else:
                            self.dv.add(np.column_stack((np.arange(len(counts)), np.array(counts))),
                                        context=self.bright_counts_context)
                        # hist = self.process_data(counts)
                        # self.plot_hist(hist, folder_name='ManifoldDetection')

                    # move fluorescence back to middle of range
                    still_there = self.rescue_ion(5.0)
                    if should_break or not still_there: break
                    #if not self.correct_cavity_drift(): break

            if should_break or ion_dead: break


    def setup_datavault(self):
        self.dark_counts_context = self.dv.context()
        self.dv.cd(['', 'Manifold Detection Counts'], True, context=self.dark_counts_context)
        self.dark_counts_dataset = self.dv.new('counts', [('run', 'arb')],
                                          [('counts', 'dark_counts', 'num')],
                                          context=self.dark_counts_context)
        self.bright_counts_context = self.dv.context()
        self.dv.cd(['', 'Manifold Detection Counts'], True, context=self.bright_counts_context)
        self.bright_counts_dataset = self.dv.new('counts_bright', [('run', 'arb')],
                                          [('counts', 'bright_counts', 'num')],
                                          context=self.bright_counts_context)


    def get_average_counts(self, num=500):
        counts = self.pmt.get_next_counts('ON', num)
        avg = np.mean(counts)
        return avg, counts

    def correct_cavity_drift(self):
        self.current_fluorescence, counts = self.get_average_counts(100)
        delta = self.current_fluorescence - self.fluorescence
        j = 0
        print("checking cavity drift")
        while np.abs(delta) > 0.2:
            if j > 10 or (self.cavity_voltage < self.cavity_rails[0], self.cavity_voltage > self.cavity_rails[1]):
                return False
            should_break = self.update_progress(0.5)
            if should_break:
                return False
            # take advantage of the fact that +voltage=red, -voltage=blue if we're red of the line
            new_cavity_voltage = self.cavity_voltage + 0.01 * np.sign(delta)
            print('Moving cavity from {} V to {} V'.format(self.cavity_voltage, new_cavity_voltage))
            self.pzt_server.set_voltage(self.cavity_chan, U(new_cavity_voltage, 'V'))
            self.cavity_voltage = new_cavity_voltage
            self.current_fluorescence, counts = self.get_average_counts(100)
            delta = self.current_fluorescence - self.fluorescence
            # time.sleep(0.5)
        return True

    def attempt_shelving(self):
        self.toggle_repump_lasers('Off')
        before_counts = np.mean(self.pmt.get_next_counts('ON', True))
        self.toggle_shelving_laser('On')
        time.sleep(0.1)
        self.toggle_shelving_laser('Off')
        after_counts = np.mean(self.pmt.get_next_counts('ON', True))
        if after_counts < before_counts * 0.7:
            print("successfully shelved")
            return True
        return False

    def rescue_ion(self, threshold):
        print("Rescuing ion")
        self.toggle_repump_lasers('On')
        self.toggle_shelving_laser('Off')
        time.sleep(10)  # should default to 10 seconds
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
            self.pulser.amplitude('411DP1', U(-46.0, 'dBm'))
        if state == 'On':
            self.pulser.amplitude('411DP1', U(-20.0, 'dBm'))# self.p.ddsDefaults.DP1_411_power)

    def finalize(self, cxn, context):
        self.toggle_repump_lasers('On')
        self.toggle_shelving_laser('Off')
        self.pmt.set_time_length(U(100, "ms"))
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = manifold_detection(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
