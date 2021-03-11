import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
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
        self.pulser = self.cxn.pulser
        self.pmt = self.cxn.normalpmtflow

    def run(self, cxn, context):

        self.setup_datavault('event_num', 'wait_time') #TODO: update this
        # self.setup_grapher('Manifold Detection')
        threshold = self.set_single_ion_threshold()
        status = True
        N = 1  # this tracks events

        self.program_pulser(single_ion_shelving_attempt)



        counts = self.pmt.get_next_counts('ON', True)
        init_time = time.time()

        # try to shelve an ion until it works
        is_shelved = False
        while is_shelved is False:
            is_shelved = self.attempt_shelving
        # set the brightness threshold

        ## START CORE LOOP

        # run for 5 minutes or until fluorescence leaves acceptable range, binning the data and outputting it to datavault

        # move fluorescence back to middle of range

        # check that the ion is still there

        # reshelve the ion

        # set new threshold (in case the other ion has a different brightness)

        ## END CORE LOOP

    def attempt_shelving(self):


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
