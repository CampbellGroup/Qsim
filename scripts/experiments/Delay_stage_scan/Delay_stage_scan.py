import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time
import numpy as np

__scriptscanner_name__ = 'Delaystagescan' # this should match the class name
class Delaystagescan(QsimExperiment):

    name = 'Ramsey Delay Stage Scan'

    exp_parameters = []
    exp_parameters.append(('Delaystagescan', 'scan'))
    exp_parameters.append(('Delaystagescan', 'average'))
    exp_parameters.append(('Delaystagescan', 'mode'))
    exp_parameters.append(('Delaystagescan', 'detuning'))
    exp_parameters.append(('Delaystagescan', 'power'))
    exp_parameters.append(('DDS_line_scan', 'Center_Frequency'))


    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.TTL = cxn.arduinottl

        self.chan = 2
        self.keithley = self.cxn.keithley_2230g_server
        self.keithley.select_device(0)

        self.pmt = self.cxn.normalpmtflow
        self.init_mode = self.pmt.getcurrentmode()
        self.pulser = cxn.pulser
        self.init_freq = self.pulser.frequency('369')
        self.init_power = self.pulser.amplitude('369')

    def run(self, cxn, context):

        '''
        Main loop
        '''
        self.set_scannable_parameters()
        self.keithley.gpib_write('Apply CH2,' + str(self.init_volt) + 'V')
        self.keithley.output(self.chan, True)
        self.pulser.frequency('369',self.WLcenter + self.detuning/2.0) # this is real laser detuning
        self.pulser.amplitude('369', self.power)
        cxn.arduinottl.ttl_output(12, False)
        self.path = self.setup_datavault('Volts', 'kcounts/sec')
        self.setup_grapher('Ramsey Delay Stage Piezo Scan')
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
            self.keithley.gpib_write('APPLy CH2,' + str(volt) + 'V')  # we write direct GPIB for speed
            counts = self.pmt.get_next_counts(self.mode, self.average, True)
            self.dv.add(volt, counts)


    def set_scannable_parameters(self):
        '''
        gets parameters, called in run so scan works
        '''

        self.power = self.p.Delaystagescan.power
        self.WLcenter = self.p.DDS_line_scan.Center_Frequency
        self.detuning = self.p.Delaystagescan.detuning
        self.mode = self.p.Delaystagescan.mode
        self.average = int(self.p.Delaystagescan.average)
        self.x_values = self.get_scan_list(self.p.Delaystagescan.scan, 'V')
        self.init_volt = self.x_values[0]

    def finalize(self, cxn, context):
        self.pulser.frequency('369', self.init_freq)
        self.pulser.amplitude('369', self.init_power)
        cxn.arduinottl.ttl_output(12, True)
        self.pmt.set_mode(self.init_mode)
        self.keithley.gpib_write('Apply CH1,' + str(self.init_volt) + 'V')

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = Delaystagescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
