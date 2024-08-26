# -*- coding: utf-8 -*-

import labrad
from Qsim.scripts.pulse_sequences.microwave_point.microwave_ramsey_light_shift import (
    MicrowaveRamseyPoint532 as sequence,
)
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
from Qsim.scripts.experiments.Interleaved_Linescan.interleaved_linescan import (
    InterleavedLinescan,
)
from scipy.optimize import curve_fit as fit
import numpy as np

#
import time


#


class MicrowaveRamseyLightShift(QsimExperiment):
    """
        Scan delay time between microwave pulses with an interrogation pulse during the dark time,
        allowing you to measure the light shift induced by the interrogation lasers

        Pulse sequence diagram:

    Standard:
        369SP            |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        DopplerCoolingSP |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        StateDetectionSP |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        OpticalPumpingSP |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        MicrowaveTTL     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█████▁▁▁▁▁▁▁▁▁█████▁▁▁▁▁▁▁▁▁▁▁▁
        Microwave_qubit  |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▓▓▓▓▓▁▁▁▁▁▁▁▁▁▓▓▓▓▓▁▁▁▁▁▁▁▁▁▁▁▁
        532SP            |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        935SP/976SP      |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        760SP/760SP2     |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        ReadoutCount     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
             (TurnOffAll) DC          OP          RMI    ~~~~~~~~~     StandardSD

    FiberEOM:
        369SP            |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        WindfreakSynthHD |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        WindfreakSynthNV |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        MicrowaveTTL     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█████▁▁▁▁▁▁▁▁▁█████▁▁▁▁▁▁▁▁▁▁▁▁
        Microwave_qubit  |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█████▁▁▁▁▁▁▁▁▁█████▁▁▁▁▁▁▁▁▁▁▁▁
        532SP            |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        935SP/976SP      |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        760SP/760SP2     |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        ReadoutCount     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
             (TurnOffAll) DC          OP          RMI    ~~~~~~~~~     StandardSD
    """

    name = "Microwave Ramsey 532"

    exp_parameters = []
    exp_parameters.append(("DopplerCooling", "detuning"))
    exp_parameters.append(("Transitions", "main_cooling_369"))
    exp_parameters.append(("MicrowaveInterrogation", "detuning"))
    exp_parameters.append(("MicrowaveRamsey", "delay_time"))
    exp_parameters.append(("MicrowaveRamsey", "fixed_delay_time"))
    exp_parameters.append(("MicrowaveRamsey", "detuning"))
    exp_parameters.append(("MicrowaveRamsey", "scan_type"))
    exp_parameters.append(("MicrowaveRamsey", "phase_scan"))
    exp_parameters.append(("MicrowaveInterrogation", "AC_line_trigger"))
    exp_parameters.append(("MicrowaveInterrogation", "delay_from_line_trigger"))
    exp_parameters.append(("MicrowaveInterrogation", "delay_from_line_trigger"))
    exp_parameters.append(("Modes", "state_detection_mode"))
    exp_parameters.append(("ShelvingStateDetection", "repetitions"))
    exp_parameters.append(("StandardStateDetection", "repetitions"))
    exp_parameters.append(("StandardStateDetection", "points_per_histogram"))
    exp_parameters.append(("StandardStateDetection", "state_readout_threshold"))
    exp_parameters.append(("Shelving_Doppler_Cooling", "doppler_counts_threshold"))
    exp_parameters.append(("LightShift", "percent"))
    exp_parameters.append(("LightShift", "power"))

    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(("EmptySequence", "duration"))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pzt_server = cxn.piezo_server
        self.cavity_chan = 1

    def run(self, cxn, context):

        if self.p.MicrowaveInterrogation.AC_line_trigger == "On":
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(
                self.p.MicrowaveInterrogation.delay_from_line_trigger
            )

        scan_parameter = self.p.MicrowaveRamsey.scan_type
        mode = self.p.Modes.state_detection_mode

        self.p["MicrowaveInterrogation.detuning"] = self.p.MicrowaveRamsey.detuning
        self.init_line_center = None  #########
        if scan_parameter == "delay_time":
            self.cavity_voltage = self.pzt_server.get_voltage(self.cavity_chan)
            # self.init_line_center = self.run_interleaved_linescan()
            print("Initial line center at " + str(self.init_line_center))
            self.setup_datavault(
                "time", "probability"
            )  # gives the x and y names to Data Vault
            self.setup_grapher("Microwave Ramsey Experiment")
            self.dark_time = self.get_scan_list(
                self.p.MicrowaveRamsey.delay_time, "ms", shuffle=False
            )
            last_scanned = (
                time.time()
            )  # initialize time (not sure if this is the best spot to do this)
            time.sleep(2)
            for i, dark_time in enumerate(self.dark_time):
                should_break = self.update_progress(i / float(len(self.dark_time)))
                if should_break:
                    break
                self.p["EmptySequence.duration"] = U(dark_time, "ms")
                self.program_pulser(sequence)
                if mode == "Shelving":
                    [doppler_counts, detection_counts] = self.run_sequence(
                        max_runs=500, num=2
                    )
                    errors = np.where(
                        doppler_counts
                        <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold
                    )
                    counts = np.delete(detection_counts, errors)
                else:
                    [counts, counts_control] = self.run_sequence(max_runs=500, num=2)
                if i % self.p.StandardStateDetection.points_per_histogram == 0:
                    hist = self.process_data(counts)
                    self.plot_hist(hist)
                pop = self.get_pop(counts)
                pop_control = self.get_pop(counts_control)
                self.dv.add(dark_time, pop, context=self.ls_context)
                self.dv.add(dark_time, pop_control, context=self.control_context)
                if (
                    time.time() - last_scanned > 600
                ):  # linescan if it has been more than 4 minutes
                    print("Correcting Cavity Drift")
                    if self.init_line_center is None:  #######
                        self.init_line_center = self.run_interleaved_linescan()  #######
                        continue  #######
                    success = self.correct_cavity_drift()
                    last_scanned = time.time()  # update time
                    time.sleep(1)

        elif scan_parameter == "phase":
            print("not implemented")

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

        while np.abs(delta) > 1.0:

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
    exprt = MicrowaveRamseyLightShift(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
