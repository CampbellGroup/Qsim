import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time


class scan_935(QsimExperiment):

    name = '935 Scan'

    exp_parameters = []
    exp_parameters.append(('wavemeterscan', 'Port_935'))
    exp_parameters.append(('Transitions', 'repump_935'))
    exp_parameters.append(('wavemeterscan', 'scan_range_935'))
    exp_parameters.append(('wavemeterscan', 'rail_wait_time'))

    def initialize(self, cxn, context, ident):

        self.ident = ident
        print 'after cxnwlm'
        self.cxnwlm = labrad.connect('10.97.112.2', password='lab')
        self.wm = self.cxnwlm.multiplexerserver
        self.pmt = self.cxn.normalpmtflow
        self.init_mode = self.pmt.getcurrentmode()

    def run(self, cxn, context):

        self.setup_parameters()
        self.pmt.set_mode('Normal')
        self.setup_datavault('Frequency (THz)', 'kcounts/sec')
        self.currentfreq = self.currentfrequency()
        self.init_freq = 0.0
        self.low_rail = str(self.init_freq - self.scan_range['THz']/2.0)
        self.high_rail = str(self.init_freq + self.scan_range['THz']/2.0)
        self.tempdata = []
        self.wm.set_pid_course(7, self.high_rail)
        progress = 0.3
        delay = self.wait_time['s']
        self.take_data(progress, delay)
        self.wm.set_pid_course(7, self.low_rail)
        progress = 0.6
        self.take_data(progress, 2*delay)
        self.wm.set_pid_course(7, str(self.init_freq))
        progress = 0.9
        self.take_data(progress, delay)

        if len(self.tempdata) > 0:
            self.tempdata.sort()
            self.setup_grapher('Wavemeter Linescan')
            self.dv.add(self.tempdata)

        time.sleep(1)

    def take_data(self, progress, delay):
        init_time = time.time()
        while (time.time() - init_time) < delay:
            should_break = self.update_progress(progress)
            if should_break:
                self.tempdata.sort()
                self.setup_grapher('Wavemeter Linescan')
                self.dv.add(self.tempdata)
                return

            counts = self.pmt.get_next_counts('ON', 1, False)[0]
            currentfreq = self.currentfrequency()
            if currentfreq and counts:
                self.tempdata.append([1e6 * currentfreq, counts])

    def setup_parameters(self):

        self.port = int(self.p.wavemeterscan.Port_935)
        self.centerfrequency = self.p.Transitions.repump_935
        self.scan_range = self.p.wavemeterscan.scan_range_935
        self.wait_time = self.p.wavemeterscan.rail_wait_time

    def currentfrequency(self):
        try:
            absfreq = float(self.wm.get_frequency(self.port))
            currentfreq = absfreq - self.centerfrequency['THz']
            return currentfreq
        except:
            return None

    def finalize(self, cxn, context):
        self.pmt.set_mode(self.init_mode)
        self.cxnwlm.disconnect()


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = scan_935(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
