import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import time, sys
import numpy as np


class WavemeterLinescanBadWM(QsimExperiment):
    """
Logs the PMT counts as a function of the frequency on the bad wavemeter. Doesn't do any kind of scanning,
just do that manually as the experiment runs (for now, this may be implemented later)

A line center of 752.25220 THz is also curently hardcoded. This can be changed in the code of course
"""
    name = 'Wavemeter Linescan BadWM'

    exp_parameters = []

    exp_parameters.append(('Transitions', 'repump_935'))
    exp_parameters.append(('Transitions', 'repump_760'))
    exp_parameters.append(('Transitions', 'shelving_411'))
    exp_parameters.append(('Transitions', 'Hudson'))
    exp_parameters.append(('Transitions', 'repump_760_repump'))
    exp_parameters.append(('Transitions', 'repump_976'))

    exp_parameters.append(('wavemeterscan', 'scan_range_935'))
    exp_parameters.append(('wavemeterscan', 'scan_range_411'))
    exp_parameters.append(('wavemeterscan', 'scan_range_760'))
    exp_parameters.append(('wavemeterscan', 'scan_range_760_repump'))
    exp_parameters.append(('wavemeterscan', 'scan_range_976'))
    exp_parameters.append(('wavemeterscan', 'scan_range_Hudson'))

    exp_parameters.append(('wavemeterscan', 'lasername'))
    exp_parameters.append(('wavemeterscan', 'noise_floor'))
    exp_parameters.append(('wavemeterscan', 'rail_wait_time'))

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.wm = self.cxn.multiplexerserver
        # if self.p.wavemeterscan.lasername == 'Hudson':
        #    self.cxnhudwlm = labrad.connect('10.97.111.8', password='lab')
        #    self.wm = self.cxnhudwlm.multiplexerserver

    def run(self, cxn, context):

        self.setup_parameters()
        self.setup_datavault('Frequency (THz)', 'kcounts/sec')
        self.tempdata = []
        delay = self.wait_time['s']

        for i in range(100):
            progress = i / 100.0
            should_break = self.take_data(progress, delay)
            if should_break:
                return

        if len(self.tempdata) > 0:
            self.tempdata.sort()
            self.dv.add(self.tempdata)
            try:
                self.setup_grapher(self.grapher_tab)
            except KeyError:
                pass

    def take_data(self, progress, delay):
        init_time = time.time()
        while (time.time() - init_time) < delay:
            should_break = self.update_progress(progress)
            if should_break:
                self.tempdata.sort()
                self.dv.add(self.tempdata)
                try:
                    self.setup_grapher(self.grapher_tab)
                except KeyError:
                    pass
                return True

            counts = self.pmt.get_next_counts('ON', 1, False)[0]
            currentfreq = self.currentfrequency()
            if currentfreq:
                self.tempdata.append([1e6 * currentfreq, counts])

    def setup_parameters(self):
        self.wait_time = self.p["wavemeterscan.rail_wait_time"]
        self.centerfrequency = U(812.12787, 'THz')
        self.grapher_tab = '976_linescan'

    def currentfrequency(self):
        try:
            absfreq = float(self.wm.get_frequency(0))
            currentfreq = absfreq - self.centerfrequency['THz']
            # if (currentfreq <= -0.01) or (currentfreq >= 0.01):
            #     currentfreq = None
            return currentfreq
        except:
            return None


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = WavemeterLinescanBadWM(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
