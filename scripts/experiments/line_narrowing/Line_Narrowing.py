import labrad
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from Qsim.scripts.experiments.wavemeter_linescan.wavemeter_linescan import wavemeter_linescan
from labrad.units import WithUnit
import time
import socket
import numpy as np

class Line_Narrowing(experiment):

    name = 'Line_Narrowing'

    exp_parameters = []
    exp_parameters.append(('Line_Narrowing', 'voltage_scan'))
    exp_parameters.append(('Line_Narrowing', 'direction'))

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
        self.wmlinescan = self.make_experiment(wavemeter_linescan)
        self.wmlinescan.initialize(cxn, context,ident)
        self.cxn = labrad.connect(name='Line_narrowing exp')
        self.dv = self.cxn.data_vault
        self.grapher = self.cxn.grapher
        self.mps = self.cxn.multipole_server
        self.init_multipoles = cxn.multipole_server.get_multipoles()
        self.p = self.parameters

    def run(self, cxn, context):

        '''
        Main loop
        '''
        min, max, steps = self.p.Line_Narrowing.voltage_scan
        direction = self.p.Line_Narrowing.direction
        scan = np.linspace(min, max, steps)
        scan = [pt for pt in scan]
        multipoles = np.array(self.init_multipoles)
        if direction == 'Ex':
            multipoleindex = 0
        elif direction == 'Ey':
            multipoleindex = 1
        else:
            multipoleindex = 2

        self.setup_datavault()
        for i, step in enumerate(scan):
                multipoles[multipoleindex] = step
                self.mps.set_multipoles(multipoles)
                should_stop = self.pause_or_stop()
                if should_stop:
                    break
                self.wmlinescan.run(cxn, context,
                                    append=' ' + direction + ' ' + str(step) + ' ')
                progress = 100*float(i)/steps
                self.sc.script_set_progress(self.ident, progress)

    def setup_datavault(self):

        '''
        Adds parameters to datavault and parameter vault
        '''
        pass

#        self.dv.cd('Line Narrowing', True)
#        dataset = self.dv.new('ML Piezo Scan', [('Volt', 'num')],
#                              [('kilocounts/sec', '', 'num')])
#        self.grapher.plot(dataset, 'ML Piezo Scan', False)
#        self.dv.add_parameter('scan', self.scan)
#        self.dv.add_parameter('average', self.average)

    def finalize(self, cxn, context):
        self.mps.set_multipoles(self.init_multipoles)
        self.cxn.disconnect()


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = Line_Narrowing(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
