import labrad
import numpy as np
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from treedict import TreeDict
from labrad.units import WithUnit
import time


class metastable_transition(experiment):

    name = 'Meta-Stable Transition'

    exp_parameters = []
    exp_parameters.append(('metastable', 'M2_scan'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.dv = cxn.data_vault
        self.mps = cxn.multipole_server
        self.init_multipoles = cxn.multipole_server.get_multipoles()

    def run(self, cxn, context):
        minim, maxim, steps = self.parameters.metastable.M2_scan
        scan = np.linspace(minim['V'], maxim['V'], steps)
        scan = [WithUnit(pt, 'V') for pt in scan]
        multipoles = np.array(self.init_multipoles)
        for i, setting in enumerate(scan):
            time.sleep(0.1)
            should_stop = self.pause_or_stop()
            if should_stop:
                break
            multipoles[4] = setting['V']
            self.mps.set_multipoles(multipoles)
            progress = 100*float(i)/steps
            self.sc.script_set_progress(self.ident, progress)
        self.saveData()

    def saveData(self):
        self.dv.cd(['','metastable'],True)

    def finalize(self, cxn, context):
        self.mps.set_multipoles(self.init_multipoles)

if __name__ == '__main__':
    #normal way to launch
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = metastable_transition(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)