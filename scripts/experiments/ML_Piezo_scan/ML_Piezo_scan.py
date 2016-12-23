import labrad
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from labrad.units import WithUnit
import time
import socket
import numpy as np

class MLpiezoscan(experiment):

    name = 'ML Piezo Scan'

    exp_parameters = []
    exp_parameters.append(('MLpiezoscan', 'scan'))
    exp_parameters.append(('MLpiezoscan', 'average'))
    exp_parameters.append(('MLpiezoscan', 'mode'))
    exp_parameters.append(('MLpiezoscan', 'detuning'))
    exp_parameters.append(('wavemeterscan', 'Center_Frequency_369'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.cxnwlm = labrad.connect('10.97.112.2', password = 'lab')
        self.cxn = labrad.connect(name='MLpiezoscan')
        self.locker = self.cxn.single_wm_lock_server
        self.dv = self.cxn.data_vault
        self.dv.cd('ML Piezo Scan', True)
        self.grapher = self.cxn.graper
        self.wm = self.cxnwlm.multiplexerserver
        self.pmt = self.cxn.normalpmtflow
        self.shutter = self.cxn.arduinottl
        self.init_mode = self.pmt.getcurrentmode()
        self.p = self.parameters
        self.chan = 2

    def run(self, cxn, context):

        '''
        Main loop
        '''
        self.set_scannable_parameters()
        self.locker.set_point(self.WLcenter['THz'] + self.detuning['THz'])
        time.sleep(1.0)
        if self.mode == 'DIFF':
            self.pmt.set_mode('Differential')
        else:
            self.pmt.set_mode('Normal')
        self.setup_datavault()
        for i, volt in enumerate(self.xvalues):
                should_stop = self.pause_or_stop()
                if should_stop:
                    break
                self.wm.set_dac_voltage(self.chan, volt)
                counts = self.pmt.get_next_counts(self.mode, self.average, True)
                self.dv.add(volt, counts)
                progress = 100*float(i)/self.numberofsteps
                self.sc.script_set_progress(self.ident, progress)

    def set_scannable_parameters(self):
        '''
        gets parameters, called in run so scan works
        '''

        self.WLcenter = self.p.wavemeterscan.Center_Frequency_369
        self.detuning = self.p.MLpiezoscan.detuning
        self.mode = self.p.MLpiezoscan.mode
        self.scan = self.p.MLpiezoscan.scan
        self.average = int(self.p.MLpiezoscan.average)
        self.minval = self.p.MLpiezoscan.scan[0]['V']
        self.maxval = self.p.MLpiezoscan.scan[1]['V']
        self.numberofsteps = int(self.p.MLpiezoscan.scan[2])
        self.xvalues = np.linspace(self.minval, self.maxval, self.numberofsteps)

    def setup_datavault(self):

        '''
        Adds parameters to datavault and parameter vault
        '''

        dataset = self.dv.new('ML Piezo Scan', [('Volt', 'num')],
                              [('kilocounts/sec', '', 'num')])
        self.grapher.plot(dataset, 'ML Piezo Scan', False)
        self.dv.add_parameter('scan', self.scan)
        self.dv.add_parameter('average', self.average)
        self.dv.add_parameter('detuning', self.detuning)

    def finalize(self, cxn, context):
        self.pmt.set_mode(self.init_mode)
        self.cxn.disconnect()

    def volt_to_bit(self, volt):
        minval = -15.
        maxval = 15.
        m = (2**16 - 1)/(maxval - minval)
        b = -1 * minval * m
        bit = int(m*volt + b)
        return bit


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MLpiezoscan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
