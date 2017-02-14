import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time
import os


class MLpiezoscan(QsimExperiment):

    name = 'ML Piezo Scan'

    exp_parameters = []
    exp_parameters.append(('MLpiezoscan', 'scan'))
    exp_parameters.append(('MLpiezoscan', 'average'))
    exp_parameters.append(('MLpiezoscan', 'mode'))
    exp_parameters.append(('MLpiezoscan', 'detuning'))
    exp_parameters.append(('wavemeterscan', 'Center_Frequency_369'))

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.cxnwlm = labrad.connect('10.97.112.2',
                                     password=os.environ['LABRADPASSWORD'])
        self.TTL = cxn.arduinottl
        self.locker = self.cxn.single_wm_lock_server
        self.wm = self.cxnwlm.multiplexerserver
        self.pmt = self.cxn.normalpmtflow
        self.shutter = self.cxn.arduinottl
        self.init_mode = self.pmt.getcurrentmode()
        self.chan = 2

    def run(self, cxn, context):

        '''
        Main loop
        '''
        self.set_scannable_parameters()
        self.locker.set_point(self.WLcenter['THz'] + self.detuning['THz'])
        time.sleep(1.0)
        cxn.arduinottl.ttl_output(12, False)
        self.setup_datavault('Volts', 'kcounts/sec')
        self.setup_grapher('ML Piezo Scan')
        try:
            MLfreq = cxn.bristol_521.get_wavelength()
            self.dv.add_parameter('Bristol Reading', MLfreq)
        except:
            pass

        if self.mode == 'DIFF':
            self.pmt.set_mode('Differential')
        else:
            self.pmt.set_mode('Normal')

        for i, volt in enumerate(self.x_values):
            should_break = self.update_progress(i/float(len(self.x_values)))
            if should_break:
                break
            self.wm.set_dac_voltage(self.chan, volt)
            counts = self.pmt.get_next_counts(self.mode, self.average, True)
            self.dv.add(volt, counts)

    def set_scannable_parameters(self):
        '''
        gets parameters, called in run so scan works
        '''

        self.WLcenter = self.p.wavemeterscan.Center_Frequency_369
        self.detuning = self.p.MLpiezoscan.detuning
        self.mode = self.p.MLpiezoscan.mode
        self.average = int(self.p.MLpiezoscan.average)
        self.x_values = self.get_scan_list(self.p.MLpiezoscan.scan, 'V')

    def finalize(self, cxn, context):
        cxn.arduinottl.ttl_output(12, True)
        self.pmt.set_mode(self.init_mode)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MLpiezoscan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
