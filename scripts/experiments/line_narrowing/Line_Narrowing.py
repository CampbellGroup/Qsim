import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.interleaved_linescan.interleaved_linescan import InterleavedLinescan
import numpy as np


class Line_Narrowing(QsimExperiment):

    name = 'Line_Narrowing'

    exp_parameters = []
    exp_parameters.append(('Line_Narrowing', 'voltage_scan'))
    exp_parameters.append(('Line_Narrowing', 'direction'))

    def initialize(self, cxn, context, ident):

        self.multipole_names = {'Ex': 0, 'Ey': 1, 'Ez': 2}
        self.ident = ident
        self.linescan = self.make_experiment(InterleavedLinescan)
        self.linescan.initialize(cxn, context, ident)
        self.mps = self.cxn.multipole_server
        self.init_multipoles = cxn.multipole_server.get_multipoles()

    def run(self, cxn, context):

        '''
        Main loop
        '''

        self.setup_parameters()
        x_values = self.get_scan_list(self.p.Line_Narrowing.voltage_scan, units=None)

        for i, step in enumerate(x_values):

            should_break = self.update_progress(i/float(len(x_values)))
            if should_break:
                break

            self.multipoles[self.multipole_index] = step
            self.mps.set_multipoles(self.multipoles)
            self.linescan.run(cxn, context)
            self.linescan.dv.add_parameter(self.multipole_direction, step)

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
