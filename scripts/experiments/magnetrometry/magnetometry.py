import labrad
from labrad.units import Unit
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.Microwave_Linescan.microwave_linescan import (
    MicrowaveLineScan,
)
import numpy as np
from scipy.optimize import curve_fit


class Magnetometry(QsimExperiment):
    # TODO: magnetometry tab in grapher

    name = "Magnetometry"

    exp_parameters = []
    exp_parameters.append(("magnetometry", "current_scan_x"))
    exp_parameters.append(("magnetometry", "current_scan_y"))
    exp_parameters.append(("magnetometry", "current_scan_z"))
    exp_parameters.append(("magnetometry", "direction"))
    exp_parameters.append(MicrowaveLineScan.all_required_parameters())

    def sincsq(x, a, b, c, d):
        return a * np.sinc(b * x - c) ** 2 + d

    def initialize(self, cxn, context, ident):
        self.coil_names = {"Bx": 0, "By": 1, "Bz": 2}
        self.ident = ident
        self.linescan = self.make_experiment(MicrowaveLineScan)
        self.linescan.initialize(cxn, context, ident)
        self.ks = self.cxn.Keithley_Server
        self.init_currents = np.array(
            cxn.Keithley_Server.get_applied_voltage_current(2)
        )

    def run(self, cxn, context):
        self.setup_datavault("current (A)", "center frequency (MHz)")
        self.setup_grapher("magnetometry")  # sets up the grapher tab
        self.setup_parameters()
        if self.coil_direction == "Bx":
            x_values = self.get_scan_list(
                self.p.Magnetometry.current_scan_x, units=Unit("A")
            )
        elif self.coil_direction == "By":
            x_values = self.get_scan_list(
                self.p.Magnetometry.current_scan_y, units=Unit("A")
            )
        elif self.coil_direction == "Bz":
            x_values = self.get_scan_list(
                self.p.Magnetometry.current_scan_z, units=Unit("A")
            )

        for i, current_step in enumerate(x_values):
            self.currents[self.coil_index] = current_step
            self.ks.all_current(self.currents)
            dataset, should_break = self.linescan.run(cxn, context)  # run the line scan
            self.linescan.dv.add_parameter(self.coil_direction, current_step)
            fitdata = dataset.get_data(
                limit=None, start=0
            )  # get the data from the linescan
            # fitdata = dv.get(limit=None, startOver=True)
            # may be that we need to navigate to the saved file in the datavault.
            xdata = [i[0] for i in fitdata]
            ydata = [i[1] for i in fitdata]
            popt, pcov = curve_fit(sincsq, xdata, ydata)  # p0=[max(ydata), 20, None]
            self.dv.add(current_step, popt[2])  # store the center position of the line
            if should_break:
                return should_break

    def setup_parameters(self):
        self.coil_direction = self.p.Magnetometry.direction
        self.coil_index = self.coil_names[self.coil_direction]
        self.currents = np.array(self.init_currents)

    def finalize(self, cxn, context):
        self.ks.all_current(self.init_currents)


if __name__ == "__main__":
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = Magnetometry(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
