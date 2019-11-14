import labrad
import labrad.units as U
from labrad.units import V, A
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.microwave_linescan.microwave_linescan import MicrowaveLinescan
import numpy as np
from scipy.optimize import curve_fit


class magnetometry(QsimExperiment):
    # TODO: Add the relevant parameters (Bx, By, Bz, direction) to the parameter vault
    # TODO: make it so self.init_currents and self.currents have units?
    # TODO: magnetometry tab in grapher

    name = 'magnetometry'

    exp_parameters = []
    exp_parameters.append(('magnetometry', 'current_scan_x'))
    exp_parameters.append(('magnetometry', 'current_scan_y'))
    exp_parameters.append(('magnetometry', 'current_scan_z'))
    exp_parameters.append(('magnetometry', 'direction'))
    exp_parameters.append(MicrowaveLinescan.all_required_parameters())

    def sincsq(x, a, b, c):
        return a*np.sinc(b*x - c)**2

    def initialize(self, cxn, context, ident):
        self.coil_names = {'Bx': 0, 'By': 1, 'Bz': 2}
        self.ident = ident
        self.linescan = self.make_experiment(MicrowaveLinescan)
        self.linescan.initialize(cxn, context, ident)
        self.ks = self.cxn.keithley_2231A_30_3
        self.init_currents = np.array(cxn.keithley_2231A_30_3.get_applied_voltage_current(2))

    def run(self, cxn, context):
        self.setup_datavault('current', 'center frequency') # gives the x and y names to datavault
        self.setup_grapher('magnetometry') # sets up the grapher tab
        self.setup_parameters()
        if   self.coil_direction == 'Bx':
            x_values = self.get_scan_list(self.p.magnetometry.current_scan_x, units=None)
        elif self.coil_direction == 'By':
            x_values = self.get_scan_list(self.p.magnetometry.current_scan_y, units=None)
        elif self.coil_direction == 'Bz':
            x_values = self.get_scan_list(self.p.magnetometry.current_scan_z, units=None)

        for i, current_step in enumerate(x_values):
            self.currents[self.coil_index] = U.WithUnit(current_step, 'A')
            self.ks.all_current(self.currents)
                # run the line scan
            dataset, should_break = self.linescan.run(cxn, context)
            self.linescan.dv.add_parameter(self.coil_direction, current_step)         
                # get the data from the linescan                      
            fitdata = dataset.get(limit=None, startOver=True)
            xdata = [i[0] for i in fitdata]
            ydata = [i[1] for i in fitdata]
                # fit the data to a sinc^2 function
            popt, pcov = curve_fit(sincsq, xdata, ydata) #p0=[max(ydata), 20, None]
                # store the center position of the line
            self.dv.add(current_step, popt[2])
            if should_break:
                return should_break

    def setup_parameters(self):
        self.coil_direction = self.p.magnetometry.direction
        self.coil_index = self.coil_names[self.coil_direction]
        self.currents = np.array(self.init_currents)

    def finalize(self, cxn, context):
        self.ks.all_current(self.init_currents)
        

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = magnetometry(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
