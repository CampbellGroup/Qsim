import labrad
from labrad.units import WithUnit
from common.lib.servers.abstractservers.script_scanner.scan_methods \
    import experiment
import numpy as np
import time


class wavemeter_linescan(experiment):

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

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.laser = self.parameters.wavemeterscan.lasername
        self.wait = self.parameters.wavemeterscan.pause_time

        if self.laser == '369':
            self.port = self.parameters.wavemeterscan.Port_369
            self.centerfrequency = \
                self.parameters.wavemeterscan.Center_Frequency_369

        elif self.laser == '399':
            self.port = self.parameters.wavemeterscan.Port_399
            self.centerfrequency = \
                self.parameters.wavemeterscan.Center_Frequency_399

        elif self.laser == '935':
            self.port = self.parameters.wavemeterscan.Port_935
            self.centerfrequency = \
                self.parameters.wavemeterscan.Center_Frequency_935

        self.cxn = labrad.connect(name='Wavemeter Line Scan')
        self.cxnwlm = labrad.connect('10.97.112.2',
                                     name='Wavemeter Scan', password='lab')
        self.wm = self.cxnwlm.multiplexerserver
        self.dv = self.cxn.data_vault
        self.dv.cd('Wavemeter Line Scan', True)
        self.grapher = self.cxn.grapher
        self.pmt = self.cxn.normalpmtflow
        self.locker = self.cxn.single_wm_lock_server
        self.init_freq = WithUnit(float(self.wm.get_frequency(self.port)), 'THz')

    def run(self, cxn, context, append=''):

        min, max, steps = self.parameters.wavemeterscan.line_scan
        scan = np.linspace(min['THz'], max['THz'], steps)
        scan = [WithUnit(pt, 'THz') for pt in scan]
        dataset = self.dv.new(append + 'Wavemeter Line Scan', [('freq', 'Hz')],
                              [('', 'Amplitude', 'kilocounts/sec')])

        self.dv.add_parameter('Frequency', self.centerfrequency)
        self.dv.add_parameter('Laser', self.laser)

        self.currentfreq = self.currentfrequency()
        tempdata = []
        self.locker.set_point(scan[0]['THz'])
        time.sleep(1.0) # allows lock to catch up
        for i, freq in enumerate(scan):
            progress = 100*float(i)/len(scan)
            self.sc.script_set_progress(self.ident, progress)
            self.locker.set_point(freq['THz'])
            time.sleep(self.wait['s'])
            should_stop = self.pause_or_stop()
            if should_stop:
                tempdata.sort()
                self.dv.add(tempdata)
                self.grapher.plot(dataset, 'spectrum', False)
                break
            counts = self.pmt.get_next_counts('ON', 1, False)[0]
            self.currentfrequency()
            if self.currentfreq and counts:
                    tempdata.append([self.currentfreq['GHz'], counts])
        tempdata.sort()
        self.dv.add(tempdata)
        time.sleep(1)
        self.grapher.plot(dataset, 'spectrum', False)

    def currentfrequency(self):
        try:
            absfreq = WithUnit(float(self.wm.get_frequency(self.port)), 'THz')
            self.currentfreq = absfreq - self.centerfrequency
        except:
            pass

    def finalize(self, cxn, context):
        self.locker.set_point(self.init_freq['THz'])
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = wavemeter_linescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
