import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time
import numpy as np


class wavemeter_linescan(QsimExperiment):

    name = 'Wavemeter Linescan'

    exp_parameters = []

    exp_parameters.append(('Transitions', 'repump_935'))
    exp_parameters.append(('Transitions', 'repump_760'))
    exp_parameters.append(('Transitions', 'shelving_411'))
    exp_parameters.append(('Transitions', 'Hudson'))
    exp_parameters.append(('Transitions', 'repump_760_repump'))
    exp_parameters.append(('Transitions', 'repump_760_repump'))
    exp_parameters.append(('Transitions', 'repump_976'))

    exp_parameters.append(('wavemeterscan', 'scan_range_935'))
    exp_parameters.append(('wavemeterscan', 'scan_range_411'))
    exp_parameters.append(('wavemeterscan', 'scan_range_760'))
    exp_parameters.append(('wavemeterscan', 'scan_range_760_repump'))
    exp_parameters.append(('wavemeterscan', 'scan_range_976'))
    exp_parameters.append(('wavemeterscan', 'scan_range_Hudson'))

    exp_parameters.append(('wavemeterscan', 'lasername'))

    exp_parameters.append(('wavemeterscan', 'rail_wait_time'))

    def initialize(self, cxn, context, ident):

        print('initializing')
        self.ident = ident
        self.cxnwlm = labrad.connect('10.97.112.2', password='lab')
        self.wm = self.cxnwlm.multiplexerserver
        # if self.p.wavemeterscan.lasername == 'Hudson':
        #    self.cxnhudwlm = labrad.connect('10.97.111.8', password='lab')
        #    self.wm = self.cxnhudwlm.multiplexerserver

    def run(self, cxn, context):

        self.setup_parameters()
        self.setup_datavault('Frequency (THz)', 'kcounts/sec')
        self.low_rail = self.centerfrequency['THz'] - self.scan_range['THz']/2.0
        self.high_rail = self.centerfrequency['THz'] + self.scan_range['THz']/2.0
        self.tempdata = []

        low_x = np.linspace(self.centerfrequency['THz'], self.low_rail, 100)
        high_x = np.linspace(self.centerfrequency['THz'], self.high_rail, 100)
        delay = self.wait_time['s']
        for i in range(100):
            progress = i/200.0
            self.take_data(progress, delay)
            self.wm.set_pid_course(self.dac_port, str(low_x[i]))

        self.wm.set_pid_course(self.dac_port, str(self.centerfrequency['THz']))
        time.sleep(5*delay)

        for i in range(100):
            progress = (100 + i)/200.0
            self.take_data(progress, delay)
            self.wm.set_pid_course(self.dac_port, str(high_x[i]))

        self.wm.set_pid_course(self.dac_port, str(self.centerfrequency['THz']))
        time.sleep(5*delay)

        if len(self.tempdata) > 0:
            self.tempdata.sort()
            self.dv.add(self.tempdata)
            try:
                if self.p.wavemeterscan.lasername in ['760', '760 (Repump)']:
                    self.setup_grapher('760_linescan')
                else:
                    self.setup_grapher(self.p.wavemeterscan.lasername + '_linescan')
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
                    self.setup_grapher(self.p.wavemeterscan.lasername + '_linescan')
                except KeyError:
                    pass
                return

            counts = self.pmt.get_next_counts('ON', 1, False)[0]
            currentfreq = self.currentfrequency()
            if currentfreq and counts:
                self.tempdata.append([1e6 * currentfreq, counts])

    def setup_parameters(self):

        if self.p.wavemeterscan.lasername == '935':
            self.centerfrequency = self.p.Transitions.repump_935
            self.scan_range = self.p.wavemeterscan.scan_range_935
            self.channel = 4
            self.dac_port = 7

        if self.p.wavemeterscan.lasername == '976':
            self.centerfrequency = self.p.Transitions.repump_976
            self.scan_range = self.p.wavemeterscan.scan_range_976
            self.channel = 7
            self.dac_port = 4

        elif self.p.wavemeterscan.lasername == '760':
            self.centerfrequency = self.p.Transitions.repump_760
            self.scan_range = self.p.wavemeterscan.scan_range_760
            self.channel = 5
            self.dac_port = 5

        elif self.p.wavemeterscan.lasername == '760 (Repump)':
            self.centerfrequency = self.p.Transitions.repump_760
            self.scan_range = self.p.wavemeterscan.scan_range_760_repump
            self.channel = 3
            self.dac_port = 6

        elif self.p.wavemeterscan.lasername == '822':
            self.centerfrequency = self.p.Transitions.shelving_411
            self.scan_range = self.p.wavemeterscan.scan_range_411
            self.channel = 3
            self.dac_port = 3

        elif self.p.wavemeterscan.lasername == 'Hudson':
           self.centerfrequency = self.p.Transitions.Hudson
           self.scan_range = self.p.wavemeterscan.scan_range_Hudson
           self.channel = 1
           self.dac_port = 1

        self.wait_time = self.p.wavemeterscan.rail_wait_time

    def currentfrequency(self):
        try:
            absfreq = float(self.wm.get_frequency(self.channel))
            currentfreq = absfreq - self.centerfrequency['THz']
            if (currentfreq <= -0.01) or (currentfreq >= 0.01):
                currentfreq = None
            return currentfreq
        except:
            return None

    def finalize(self, cxn, context):

        self.cxnwlm.disconnect()


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = wavemeter_linescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
