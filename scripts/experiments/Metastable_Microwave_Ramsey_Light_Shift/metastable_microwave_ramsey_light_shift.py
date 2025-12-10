import labrad
from Qsim.scripts.experiments.Interleaved_Linescan.interleaved_linescan import (
    InterleavedLinescan,
)

from Qsim.scripts.pulse_sequences.microwave_point.control_heralded_metastable_ramsey_light_shift_point import (
    ControlHeraldedMetastableMicrowaveRamseyLightShiftPoint as control_heralded_sequence,
)

from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np
import time


class MetastableMicrowaveRamseyLightShift(QsimExperiment):
    """ """

    name = "Metastable Microwave Ramsey Light Shift"

    exp_parameters = []
    exp_parameters.append(("MetastableMicrowaveRamseyLightShift", "interleaved_period"))
    exp_parameters.append(("ShelvingStateDetection", "state_readout_threshold"))
    exp_parameters.append(("ShelvingStateDetection", "repetitions"))
    exp_parameters.append(("MetastableStateDetection", "herald_state_prep"))

    exp_parameters.extend(control_heralded_sequence.all_required_parameters())

    exp_parameters.remove(("EmptySequence", "duration"))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pzt_server = cxn.piezo_server
        self.cavity_chan = 1
        self.heralded_number_experiments = []

    def run(self, cxn, context):

        self.p["Line_Selection.qubit"] = (
            "qubit_0"  # define the bright state prep as qubit_0
        )
        self.p["Modes.state_detection_mode"] = "Shelving"

        scan_parameter = self.p["MetastableMicrowaveRamsey.scan_type"]

        self.init_line_center = None
        if scan_parameter == "delay_time":
            self.cavity_voltage = self.pzt_server.get_voltage(self.cavity_chan)
            # self.init_line_center = self.run_interleaved_linescan()
            print("Initial line center at " + str(self.init_line_center))

            self.setup_datavault(
                "time", "probability"
            )  # gives the x and y names to Data Vault
            self.setup_grapher("Microwave Ramsey Experiment")

            self.dark_time = self.get_scan_list(
                self.p["MetastableMicrowaveRamsey.delay_time"], "ms"
            )

            last_scanned = (
                time.time()
            )  # initialize time (not sure if this is the best spot to do this)

            # Iterate through all ramsey delay times #
            for i, dark_time in enumerate(self.dark_time):
                should_break = self.update_progress(i / float(len(self.dark_time)))
                if should_break:
                    break
                self.p["EmptySequence.duration"] = U(dark_time, "ms")

                # Program and run pulse sequence with light shift and control #
                self.program_pulser(control_heralded_sequence)
                [
                    doppler_counts_LS,
                    herald_counts_LS,
                    detection_counts_LS,
                    doppler_counts_C,
                    herald_counts_C,
                    detection_counts_C,
                ] = self.run_sequence(max_runs=999, num=6)

                # Filter out data with failed deshelving and or state prep #
                all_errors_LS = np.where(
                    (
                        doppler_counts_LS
                        <= self.p["Shelving_Doppler_Cooling.doppler_counts_threshold"]
                    )
                    | (
                        herald_counts_LS
                        >= self.p["ShelvingStateDetection.state_readout_threshold"]
                    )
                )
                all_errors_C = np.where(
                    (
                        doppler_counts_C
                        <= self.p["Shelving_Doppler_Cooling.doppler_counts_threshold"]
                    )
                    | (
                        herald_counts_C
                        >= self.p["ShelvingStateDetection.state_readout_threshold"]
                    )
                )
                counts_LS = np.delete(detection_counts_LS, all_errors_LS)
                counts_C = np.delete(detection_counts_C, all_errors_C)
                print(
                    "Light Shift Percent failed to state prep: ",
                    len(all_errors_LS[0]) / len(detection_counts_LS) * 100,
                    "%",
                )
                print(
                    "Control Percent failed to state prep: ",
                    len(all_errors_C[0]) / len(detection_counts_C) * 100,
                    "%",
                )

                # add data to data vault #
                hist = self.process_data(counts_LS)
                self.plot_hist(hist)
                pop_LS = self.get_pop(counts_LS)
                pop_C = self.get_pop(counts_C)
                self.dv.add(dark_time, pop_LS, context=self.ls_context)
                self.dv.add(dark_time, pop_C, context=self.control_context)
                self.dv.add(len(counts_LS), len(counts_C), context=self.herald_context)

                # Correct Cavity Drift if "interleaved_period" time has passed #
                if (
                    time.time() - last_scanned
                    > self.p["MetastableMicrowaveRamseyLightShift.interleaved_period"][
                        "s"
                    ]
                ):
                    print("Correcting Cavity Drift")
                    if self.init_line_center is None:
                        # continue # dont do interleaved linescan
                        self.init_line_center = self.run_interleaved_linescan()
                        if self.init_line_center is True:
                            break  # if interleaved linescan returned shouldbreak==True
                        continue
                    else:
                        success = self.correct_cavity_drift()
                    last_scanned = time.time()  # update time
                    time.sleep(1)

    def run_interleaved_linescan(self):
        self.pulser.line_trigger_state(False)

        linescan_context = self.sc.context()

        self.line_tracker = self.make_experiment(InterleavedLinescan)
        self.line_tracker.initialize(self.cxn, linescan_context, self.ident)
        try:
            popt, pcov = self.line_tracker.run(self.cxn, linescan_context)
        except TypeError as e:
            return e

        print("line center {}".format(popt[0]))
        center = popt[0]
        return center

    def setup_datavault(self, x_axis, y_axis):
        """
        Adds parameters to datavault and parameter vault
        """
        self.ls_context = self.dv.context()
        self.dv.cd(["", self.name], True, context=self.ls_context)
        self.dataset = self.dv.new(
            self.name, [(x_axis, "num")], [(y_axis, "", "num")], context=self.ls_context
        )
        self.control_context = self.dv.context()
        self.dv.cd(["", self.name], True, context=self.control_context)
        self.dataset_control = self.dv.new(
            self.name + "_control",
            [(x_axis, "num")],
            [(y_axis, "", "num")],
            context=self.control_context,
        )
        self.herald_context = self.dv.context()
        self.dv.cd(["", self.name], True, context=self.herald_context)
        self.dataset_herald = self.dv.new(
            self.name + "_herald",
            [(x_axis, "LS_heralded_reps")],
            [(y_axis, "", "C_heralded_reps")],
            context=self.herald_context,
        )
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.ls_context)
        return self.dataset

    def setup_grapher(self, tab):
        if self.grapher is None:
            print("grapher not running")
        self.grapher.plot(self.dataset, tab, False)
        self.grapher.plot(self.dataset_control, tab, False)

    def lorentzian_fit(self, detuning, center, fwhm, scale, offset):
        return offset + scale * 0.5 * fwhm / (
            (detuning - center) ** 2 + (0.5 * fwhm) ** 2
        )

    def correct_cavity_drift(self):
        center_before = self.run_interleaved_linescan()
        delta = (
            self.init_line_center - center_before
        )  # cavity shift in MHz, no labrad units

        while delta > 0:

            new_cavity_voltage = self.cavity_voltage + (
                delta * 0.01
            )  # 0.01 V/ MHz on cavity
            if np.abs(new_cavity_voltage - self.cavity_voltage) < 0.5:
                self.pzt_server.set_voltage(
                    self.cavity_chan, U(new_cavity_voltage, "V")
                )
                self.cavity_voltage = new_cavity_voltage
            else:
                print("Linescan fit did not work, killing tweak up")
                break

            center_after = self.run_interleaved_linescan()
            delta = self.init_line_center - center_after

        print("Finished cavity tweak up, resuming experiment")
        return True

    def finalize(self, cxn, context):
        self.pulser.line_trigger_state(False)
        self.pulser.line_trigger_duration(U(0.0, "us"))


if __name__ == "__main__":
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MetastableMicrowaveRamseyLightShift(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
