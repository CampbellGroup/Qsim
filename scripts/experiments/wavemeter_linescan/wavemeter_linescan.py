import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time
import os


class wavemeter_linescan(QsimExperiment):

    name = 'Wavemeter Line Scan'

    exp_parameters = []
    exp_parameters.append(('wavemeterscan', 'lasername'))

    exp_parameters.append(('wavemeterscan', 'Port_369'))
    exp_parameters.append(('wavemeterscan', 'Port_399'))
    exp_parameters.append(('wavemeterscan', 'Port_935'))

    exp_parameters.append(('wavemeterscan', 'Center_Frequency_369'))
    exp_parameters.append(('wavemeterscan', 'Center_Frequency_399'))
    exp_parameters.append(('wavemeterscan', 'Center_Frequency_935'))

    exp_parameters.append(('wavemeterscan', 'line_scan'))
    exp_parameters.append(('wavemeterscan', 'pause_time'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxnwlm = labrad.connect('10.97.112.2',
                                     name='Wavemeter Scan',
                                     password=os.environ['LABRADPASSWORD'])
        self.wm = self.cxnwlm.multiplexerserver
        self.pmt = self.cxn.normalpmtflow
        self.init_mode = self.pmt.getcurrentmode()
        self.locker = self.cxn.single_wm_lock_server

    def run(self, cxn, context):

        self.setup_parameters()
        self.pmt.set_mode('Normal')
        self.init_freq = self.wm.get_frequency(self.port)
        self.setup_datavault('Frequency (THz)', 'kcounts/sec')
        self.currentfreq = self.currentfrequency()
        tempdata = []
        self.locker.set_point(self.x_values[0])
        time.sleep(1.0)  # allows lock to catch up
        for i, freq in enumerate(self.x_values):

            should_break = self.update_progress(i/float(len(self.x_values)))

            self.locker.set_point(freq)
            time.sleep(self.wait['s'])

            if should_break:
                tempdata.sort()
                self.setup_grapher('spectrum')
                self.dv.add(tempdata)
                return

            counts = self.pmt.get_next_counts('ON', 1, False)[0]
            currentfreq = self.currentfrequency()

            if currentfreq and counts:
                tempdata.append([1e6*currentfreq, counts])

        if len(tempdata) > 0:
            tempdata.sort()
            self.setup_grapher('spectrum')
            self.dv.add(tempdata)

        time.sleep(1)

    def setup_parameters(self):
        self.x_values = self.get_scan_list(self.p.wavemeterscan.line_scan, 'THz')
        self.laser = self.p.wavemeterscan.lasername
        self.wait = self.p.wavemeterscan.pause_time

        if self.laser == '369':
            self.port = int(self.p.wavemeterscan.Port_369)
            self.centerfrequency = self.p.wavemeterscan.Center_Frequency_369

        elif self.laser == '399':
            self.port = int(self.p.wavemeterscan.Port_399)
            self.centerfrequency = self.p.wavemeterscan.Center_Frequency_399

        elif self.laser == '935':
            self.port = int(self.p.wavemeterscan.Port_935)
            self.centerfrequency = self.p.wavemeterscan.Center_Frequency_935

    def currentfrequency(self):
        try:
            absfreq = float(self.wm.get_frequency(self.port))
            currentfreq = absfreq - self.centerfrequency['THz']
            return currentfreq
        except:
            return None

    def finalize(self, cxn, context):
        self.locker.set_point(self.init_freq)
        time.sleep(1)
        self.pmt.set_mode(self.init_mode)
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = wavemeter_linescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
