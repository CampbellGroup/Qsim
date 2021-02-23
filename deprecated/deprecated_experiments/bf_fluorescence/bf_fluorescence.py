"""
### BEGIN EXPERIMENT INFO
[info]
name = ion_position_tracker
load_into_scriptscanner = True
allow_concurrent = []
### END EXPERIMENT INFO
"""

import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np


class bf_fluorescence(QsimExperiment):

    name = 'bf_fluorescence'

    exp_parameters = []

    exp_parameters.append(('bf_fluorescence', 'crop_start_time'))
    exp_parameters.append(('bf_fluorescence', 'crop_stop_time'))
    exp_parameters.append(('bf_fluorescence', 'measure_time'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):
        self.setup_datavault('Time', 'kCounts')
        self.setup_grapher('bf_fluorescence')
        self.start_time = self.p.bf_fluorescence.crop_start_time['ns']
        self.stop_time = self.p.bf_fluorescence.crop_stop_time['ns']
        self.measure_time = self.p.bf_fluorescence.measure_time['ms']
        i = 0
        total_time = 0
        while True:
            timetags = self.get_timeharp_timetags(int(self.measure_time))
            total_time += self.p.bf_fluorescence.measure_time['ms']/1000
            num_cropped_timetags = sum([self.start_time <= item <= self.stop_time for item in timetags])
            self.dv.add(total_time, num_cropped_timetags/self.measure_time)
            should_break = self.update_progress(np.random.random())
            i += 1
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters
            self.start_time = self.p.bf_fluorescence.crop_start_time['ns']
            self.stop_time = self.p.bf_fluorescence.crop_stop_time['ns']
            self.measure_time = self.p.bf_fluorescence.measure_time['ms']


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = bf_fluorescence(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
