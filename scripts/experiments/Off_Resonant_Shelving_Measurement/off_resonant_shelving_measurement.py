import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import time
import numpy as np


class off_resonant_shelving_measurement(QsimExperiment):

    name = 'Off Resonant Shelving Measurement'

    exp_parameters = [
        ('ddsDefaults', 'repump_760_1_power'),
        ('ddsDefaults', 'repump_760_2_power'),
        ('ddsDefaults', 'DP411_power')
    ]

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.pulser = self.cxn.pulser
        self.pmt = self.cxn.normalpmtflow

    def run(self, cxn, context):
        '''
        Way that this experiment is written, the 411 nm and 760 nm lasers must be on at the beginning
        '''

        self.setup_datavault('event_num', 'wait_time')
        self.setup_grapher('Off Resonant Shelving Measurement')
        threshold = 5.0
        status = True
        N = 1  # this tracks events
        while status:
            init_time = time.time()  # start of the particular run
            counts = self.pmt.get_next_counts('ON', True)
            should_break = self.update_progress(np.random.random())
            if should_break:
                break

            self.toggle_shelving_laser('On')
            self.toggle_repump_lasers('Off')

            while counts > threshold:
                should_break = self.update_progress(np.random.random())
                if should_break:
                    break
                counts = self.pmt.get_next_counts('ON', True)

            time.sleep(2.0)
            check_ion = self.pmt.get_next_counts('ON', True)
            if check_ion < threshold:
                # ensures that ion was actually in F state, not just a collision
                self.dv.add(N, time.time() - init_time - 2.0)

            status = self.rescue_ion(threshold)
            N += 1

    def rescue_ion(self, threshold):
        self.toggle_repump_lasers('On')
        self.toggle_shelving_laser('Off')
        time.sleep(10.0)
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
