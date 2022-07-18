"""
### BEGIN EXPERIMENT INFO
[info]
name = dacRaster
load_into_scriptscanner = True
allow_concurrent = []
### END EXPERIMENT INFO
"""

import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time
import numpy as np


class dacRaster(QsimExperiment):
    """
    This experiment will scan through a user specified list of DAC voltages and can be run when
    first trying to load the trap, or if the loadable position in the trap has been lost.
    """
    name = 'DAC Raster'

    exp_parameters = []
    exp_parameters.append(('dacraster', 'voltage_scan_x'))
    exp_parameters.append(('dacraster', 'voltage_scan_y'))
    exp_parameters.append(('dacraster', 'voltage_scan_z'))
    exp_parameters.append(('dacraster', 'Pause_Time'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.mps = self.cxn.multipole_server
        self.init_multipoles = cxn.multipole_server.get_multipoles()
        self.multipoles = np.array(self.init_multipoles)
        self.Xvalues = self.get_scan_list(self.p.dacraster.voltage_scan_x, units=None)
        self.Yvalues = self.get_scan_list(self.p.dacraster.voltage_scan_y, units=None)
        self.Zvalues = self.get_scan_list(self.p.dacraster.voltage_scan_z, units=None)

        self.totalstep = (len(self.Xvalues))*(len(self.Yvalues))*(len(self.Zvalues))

    def run(self, cxn, context):

        for xvoltage in self.Xvalues:
            self.changevoltage('X', xvoltage)
            for yvoltage in self.Yvalues:
                self.changevoltage('Y', yvoltage)
                for i, zvoltage in enumerate(self.Zvalues):
                    self.changevoltage('Z', zvoltage)
                    should_break = self.update_progress(i/float(len(self.Zvalues)))
                    if should_break:
                        return should_break
                    time.sleep(self.parameters.dacraster.Pause_Time['s'])

    def changevoltage(self, direction, voltage):

        if direction == 'X':
            self.multipoles[2] = voltage
            self.mps.set_multipoles(self.multipoles)
        elif direction == 'Y':
            self.multipoles[0] = voltage
            self.mps.set_multipoles(self.multipoles)
        elif direction == 'Z':
            self.multipoles[1] = voltage
            self.mps.set_multipoles(self.multipoles)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = dacRaster(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
