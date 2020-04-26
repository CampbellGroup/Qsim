import labrad
import time
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment


class scan_multipole(QsimExperiment):

    name = 'Scan Multipole'

    exp_parameters = []
    exp_parameters.append(('scan_multipole', 'Multipole'))
    exp_parameters.append(('scan_multipole', 'Range'))
    exp_parameters.append(('scan_multipole', 'pause_time'))

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.mps = cxn.multipole_server
        self.init_multipoles = list(self.mps.get_multipoles())
        self.index_dict = {'Ex': 0, 'Ey': 1, 'Ez': 2, 'M1':3,'M2': 4, 'M3': 5, 'M4': 6, 'M5':7}

    def run(self, cxn, context):

        self.multipole_index = self.index_dict[self.p.scan_multipole.Multipole]
        self.x_values = self.get_scan_list(self.p.scan_multipole.Range, units=None)
        self.multipoles = self.init_multipoles

        for i, x_point in enumerate(self.x_values):
            self.multipoles[self.multipole_index] = x_point
            should_break = self.update_progress(i/float(len(self.x_values)))
            if should_break:
                break

            self.mps.set_multipoles(self.multipoles)
            time.sleep(self.p.scan_multipole.pause_time['s'])

    def finalize(self, cxn, context):
        pass

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = scan_multipole(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
