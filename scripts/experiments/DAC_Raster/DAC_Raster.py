'''
Created on Jun 16, 2016

@author: qsimexpcontrol
'''

import labrad
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from labrad.units import WithUnit
import time
import numpy as np


class dacRaster(experiment):

    name = 'DAC Raster'

    exp_parameters = []

    exp_parameters.append(('dacraster', 'X_Voltage'))
    exp_parameters.append(('dacraster', 'Y_Voltage'))
    exp_parameters.append(('dacraster', 'DC_Offset_Voltage'))

    exp_parameters.append(('dacraster', 'Scan_X'))
    exp_parameters.append(('dacraster', 'Scan_Y'))
    exp_parameters.append(('dacraster', 'Scan_DC'))

    exp_parameters.append(('dacraster', 'Pause_Time'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.dac = cxn.arduinodac

        self.Xminval = self.parameters.dacraster.X_Voltage[0]['V']
        self.Xmaxval = self.parameters.dacraster.X_Voltage[1]['V']
        self.Xnumberofsteps = int(self.parameters.dacraster.X_Voltage[2])
        print self.Xminval, self.Xmaxval, self.Xnumberofsteps
        self.Xstepsize = (float(self.Xmaxval) - self.Xminval)/(self.Xnumberofsteps - 1)
        self.Xvalues = np.linspace(self.Xminval, self.Xmaxval,
                                   self.Xnumberofsteps)

        self.Yminval = self.parameters.dacraster.Y_Voltage[0]['V']
        self.Ymaxval = self.parameters.dacraster.Y_Voltage[1]['V']
        self.Ynumberofsteps = int(self.parameters.dacraster.Y_Voltage[2])
        self.Ystepsize = int((float(self.Ymaxval) - self.Yminval)/(self.Ynumberofsteps - 1))
        self.Yvalues = np.linspace(self.Yminval, self.Ymaxval,
                                   self.Ynumberofsteps)

        self.DCminval = self.parameters.dacraster.DC_Offset_Voltage[0]['V']
        self.DCmaxval = self.parameters.dacraster.DC_Offset_Voltage[1]['V']
        self.DCnumberofsteps = int(self.parameters.dacraster.DC_Offset_Voltage[2])
        self.DCstepsize = int((float(self.DCmaxval) - self.DCminval)/(self.DCnumberofsteps - 1))
        self.DCvalues = np.linspace(self.DCminval, self.DCmaxval,
                              self.DCnumberofsteps)

        self.totalstep = (self.Xnumberofsteps)  * (self.Ynumberofsteps ) * (self.DCnumberofsteps )

        if self.parameters.dacraster.Scan_DC:
            self.lowestaxis = 'DC'
        elif self.parameters.dacraster.Scan_Y:
            self.lowestaxis = 'Y'
        else:
            self.lowestaxis = 'X'

        self.step = 0

    def run(self, cxn, context):

        for xvoltage in self.Xvalues:
            self.currentxvolt = xvoltage
            self.changevoltage('X', xvoltage)
            for yvoltage in self.Yvalues:
                self.currentyvolt = yvoltage
                self.changevoltage('Y', yvoltage)
                for dcvoltage in self.DCvalues:
                    self.changevoltage('DC', dcvoltage)
                    should_stop = self.pause_or_stop()
                    if should_stop:
                        return

    def dacoutput(self, voltage):
        output = int(255/25.4 * (voltage) + 127.5)
        return output

    def changevoltage(self, direction, voltage):
        output = self.dacoutput(voltage)
        minusoutput = self.dacoutput(-voltage)
        print direction, voltage
        if output > 255:
            output = 255
        elif output < 0:
            output = 0
        if direction == 'X':
            self.dac.dacoutput(1, output)
            self.dac.dacoutput(2, minusoutput)

        elif direction == 'Y':
            self.dac.dacoutput(3, output)
            self.dac.dacoutput(5, minusoutput)

        elif direction == 'DC':

            self.dac.dacoutput(1, self.dacoutput(self.currentxvolt + voltage))
            self.dac.dacoutput(2, self.dacoutput(-self.currentxvolt + voltage))
            self.dac.dacoutput(3, self.dacoutput(self.currentyvolt + voltage))
            self.dac.dacoutput(5, self.dacoutput(-self.currentyvolt + voltage))

        if direction != self.lowestaxis:
            pass
        else:
            self.step += 1
        self.progress = 100*float(self.step)/(self.totalstep)
        time.sleep(self.parameters.dacraster.Pause_Time['s'])
        if self.progress >= 100.0:
            self.progress = 100.0
        self.sc.script_set_progress(self.ident, self.progress)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = dacRaster(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
