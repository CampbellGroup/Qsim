import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.Interleaved_Linescan.interleaved_linescan import interleaved_linescan
import numpy as np


class line_narrowing(QsimExperiment):
    """
    Repeats the interleaved linescan experiment at different (x, y, z) electric
    field multipoles specified by the user. Helpful for micromotion compensation
    """

    name = 'Line Narrowing'

    exp_parameters = []
    exp_parameters.append(('Line_Narrowing', 'voltage_scan_x'))
    exp_parameters.append(('Line_Narrowing', 'voltage_scan_y'))
    exp_parameters.append(('Line_Narrowing', 'voltage_scan_z'))
    exp_parameters.append(('Line_Narrowing', 'direction'))
    exp_parameters.extend(interleaved_linescan.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.multipole_names = {'Ex': 2, 'Ey': 0, 'Ez': 1}
        self.ident = ident
        self.linescan = self.make_experiment(interleaved_linescan)
        self.linescan.initialize(cxn, context, ident)
        self.mps = self.cxn.multipole_server
        self.init_multipoles = cxn.multipole_server.get_multipoles()

    def run(self, cxn, context):

        '''
        Main loop
        '''

        self.setup_parameters()
        if self.multipole_direction == 'Ex':
            x_values = self.get_scan_list(self.p.Line_Narrowing.voltage_scan_x, units=None)
        elif self.multipole_direction == 'Ey':
            x_values = self.get_scan_list(self.p.Line_Narrowing.voltage_scan_y, units=None)
        elif self.multipole_direction == 'Ez':
            x_values = self.get_scan_list(self.p.Line_Narrowing.voltage_scan_z, units=None)

        for i, step in enumerate(x_values):
            self.multipoles[self.multipole_index] = step
            self.mps.set_multipoles(self.multipoles)
            detuning, counts = self.linescan.run(cxn, context)
            self.linescan.dv.add_parameter(self.multipole_direction, step)
            should_break = self.update_progress(i/float(len(x_values)))
            if should_break:
                return should_break

    def setup_parameters(self):

        self.multipole_direction = self.p.Line_Narrowing.direction
        self.multipole_index = self.multipole_names[self.multipole_direction]
        self.multipoles = np.array(self.init_multipoles)

    def finalize(self, cxn, context):
        self.mps.set_multipoles(self.init_multipoles)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = line_narrowing(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
