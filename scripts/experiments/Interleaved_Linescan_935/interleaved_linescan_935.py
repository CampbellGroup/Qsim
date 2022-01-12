import labrad
from labrad.units import WithUnit as U
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time
import numpy as np


class interleaved_linescan_935(QsimExperiment):

    name = 'Interleaved Linescan 935'

    exp_parameters = []

    exp_parameters.append(('Transitions', 'repump_935'))

    exp_parameters.append(('InterleavedScan935', 'scan_range'))
    exp_parameters.append(('InterleavedScan935', 'rescue_time'))
    exp_parameters.append(('InterleavedScan935', 'rail_wait_time'))
    exp_parameters.append(('InterleavedScan935', 'repump_power'))

    def initialize(self, cxn, context, ident):

        print('initializing')
        self.ident = ident
        self.cxnwlm = labrad.connect('10.97.112.2', password='lab')
        self.wm = self.cxnwlm.multiplexerserver
        self.probe_AOM_chan = '976SP'
        self.repump_AOM_chan = '935SP'

    def run(self, cxn, context):

        self.setup_parameters()
        self.setup_datavault('Frequency (THz)', 'kcounts/sec')
        self.low_rail = self.centerfrequency['THz'] - self.scan_range['THz']/2.0
        self.high_rail = self.centerfrequency['THz'] + self.scan_range['THz']/2.0
        self.tempdata = []

        low_x = np.linspace(self.centerfrequency['THz'], self.low_rail, 100)
        high_x = np.linspace(self.centerfrequency['THz'], self.high_rail, 100)
        delay = self.wait_time['s']

        self.pulser.amplitude(self.repump_AOM_chan, self.repump_power, context=self.context)

        for i in range(100):
            progress = i/200.0
            self.take_data(progress, delay)
            self.wm.set_pid_course(self.probe_dac_port, str(low_x[i]))
            self.rescue_ion(self.rescue_time['s'])
            self.check_break(progress)

        self.wm.set_pid_course(self.probe_dac_port, str(self.centerfrequency['THz']))
        self.pulser.amplitude(self.repump_AOM_chan, U(-8.0, 'dBm'), context=self.context)
        # time.sleep(5*delay)
        time.sleep(10)
        self.pulser.amplitude(self.repump_AOM_chan, self.repump_power, context=self.context)


        for i in range(100):
            progress = (100 + i)/200.0
            self.take_data(progress, delay)
            self.wm.set_pid_course(self.probe_dac_port, str(high_x[i]))
            self.rescue_ion(self.rescue_time['s'])
            self.check_break(progress)

        self.wm.set_pid_course(self.probe_dac_port, str(self.centerfrequency['THz']))
        self.pulser.amplitude(self.repump_AOM_chan, U(-8.0, 'dBm'), context=self.context)
        time.sleep(5*delay)

        if len(self.tempdata) > 0:
            self.tempdata.sort()
            self.dv.add(self.tempdata)
            try:
                self.setup_grapher('935_linescan')
            except KeyError:
                pass

    def rescue_ion(self, delay):
        self.pulser.amplitude(self.repump_AOM_chan, U(-8.0, 'dBm'), context=self.context)
        time.sleep(delay)
        self.pulser.amplitude(self.repump_AOM_chan, self.repump_power, context=self.context)
        time.sleep(0.3)


    def take_data(self, progress, delay):
        init_time = time.time()
        while (time.time() - init_time) < delay:
            self.check_break(progress)
            should_break = self.update_progress(progress)
            if should_break:
                self.tempdata.sort()
                self.dv.add(self.tempdata)
                try:
                    self.setup_grapher('935_linescan')
                except KeyError:
                    pass
                return

            counts = self.pmt.get_next_counts('ON', 1, False)[0]
            currentfreq = self.currentfrequency()
            if currentfreq and counts:
                self.tempdata.append([1e6 * currentfreq, counts])

    def check_break(self, progress):
        should_break = self.update_progress(progress)
        if should_break:
            self.tempdata.sort()
            self.dv.add(self.tempdata)
            try:
                self.setup_grapher('935_linescan')
            except KeyError:
                pass
            return

    def setup_parameters(self):

        self.probe_channel = 7
        self.probe_dac_port = 4
        self.pump_channel = 4
        self.pump_dac_port = 7
        self.centerfrequency = self.p.Transitions.repump_935
        self.scan_range = self.p.InterleavedScan935.scan_range
        self.rescue_time = self.p.InterleavedScan935.rescue_time
        self.wait_time = self.p.InterleavedScan935.rail_wait_time
        self.repump_power = self.p.InterleavedScan935.repump_power

    def currentfrequency(self):
        try:
            absfreq = float(self.wm.get_frequency(self.probe_channel))
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
    exprt = interleaved_linescan_935(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
