import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.wavemeter_linescan.wavemeter_linescan import wavemeter_linescan
import numpy as np


class Line_Narrowing(QsimExperiment):

    name = 'Line_Narrowing'

    exp_parameters = []
    exp_parameters.append(('Line_Narrowing', 'voltage_scan'))
    exp_parameters.append(('Line_Narrowing', 'direction'))

    exp_parameters.append(('wavemeterscan', 'lasername'))
    exp_parameters.append(('wavemeterscan', 'Port_369'))
    exp_parameters.append(('wavemeterscan', 'Center_Frequency_369'))
    exp_parameters.append(('wavemeterscan', 'line_scan'))
    exp_parameters.append(('wavemeterscan', 'pause_time'))

    def initialize(self, cxn, context, ident):

        self.multipole_names = {'Ex': 0, 'Ey': 1, 'Ez': 2}
        self.ident = ident
        self.wmlinescan = self.make_experiment(wavemeter_linescan)
        self.wmlinescan.initialize(cxn, context, ident)
        self.mps = self.cxn.multipole_server
        self.init_multipoles = cxn.multipole_server.get_multipoles()

    def run(self, cxn, context):

        '''
        Main loop
        '''

        self.setup_parameters()
        x_values = self.get_scan_list(self.p.Line_Narrowing.voltage_scan)

        for i, step in enumerate(x_values):

            should_break = self.update_progress(i/float(len(self.x_values)))
            if should_break:
                break

            self.multipoles[self.multipole_index] = step
            self.mps.set_multipoles(self.multipoles)
            self.wmlinescan.run(cxn, context)
            self.wmlinescan.dv.add_parameter(self.multipole_direction, step)

    def setup_parameters(self):

        self.multipole_direction = self.p.Line_Narrowing.direction
        self.multipole_index = self.multipole_names[self.multipole_direction]
        self.multipoles = np.array(self.init_multipoles)

    def finalize(self, cxn, context):
        self.mps.set_multipoles(self.init_multipoles)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = Line_Narrowing(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
