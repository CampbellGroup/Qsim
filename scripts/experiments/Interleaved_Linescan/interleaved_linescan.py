# -*- coding: utf-8 -*-

import labrad
import numpy as np
from labrad.units import WithUnit as U
from scipy.optimize import curve_fit

from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.pulse_sequences.interleaved_point import InterleavedPoint


class InterleavedLinescan(QsimExperiment):
    """
    Scan the 369 laser with the AOM double pass interleaved with Doppler cooling to reveal the lineshape.
    This experiment helps to diagnose problems with micromotion compensation and cooling laser intensity

    Pulse sequence diagram:

    Standard
        369DP             |████████████████████████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
        DopplerCoolingSP  |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        935SP/976SP       |████████████████████████████████████████████████
        760SP/760SP2      |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        TimeResolvedCount |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████████████████
              (TurnOffAll) DopplerCooling          DipoleInterrogation

    FiberEOM
        369DP             |████████████████████████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
        SynthHD           |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        935SP/976SP       |████████████████████████████████████████████████
        760SP/760SP2      |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        TimeResolvedCount |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████████████████
              (TurnOffAll) DopplerCooling          DipoleInterrogation

    """

    name = "Interleaved Line Scan"

    exp_parameters = []
    exp_parameters.append(("InterleavedLinescan", "repititions"))
    exp_parameters.append(("InterleavedLinescan", "line_scan"))
    exp_parameters.append(("DopplerCooling", "detuning"))
    exp_parameters.append(("Transitions", "main_cooling_369"))

    exp_parameters.extend(InterleavedPoint.all_required_parameters())
    exp_parameters.remove(("DipoleInterrogation", "frequency"))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.reg = cxn.registry
        self.pulser = cxn.pulser
        self.fit_guess = [5.0, 27.0, 3500.0, 0.0]
        self.reg.cd(["", "settings"])

    def run(self, cxn, context):
        self.pulser.line_trigger_state(False)
        self.setup_datavault(
            "frequency", "photons"
        )  # gives the x and y names to Data Vault
        self.setup_grapher("Interleaved Linescan")
        self.detunings = self.get_scan_list(
            self.p["InterleavedLinescan.line_scan"], "MHz"
        )
        return_detuning, return_counts = [], []
        for i, detuning in enumerate(self.detunings):
            if context == (0, 2):
                should_break = self.update_progress(i / float(len(self.detunings)))
                if should_break:
                    return should_break
            # self.p["Transitions.main_cooling_369"] divide by 2 for the double pass
            freq = U(detuning, "MHz") / 2.0 + self.p["ddsDefaults.DP369_freq"]
            track_detuning, track_counts = self.program_pulser(freq, detuning)
            return_detuning.append(track_detuning)
            return_counts.append(track_counts)

        # skip first couple points of data since they occasionally come in at random values
        # after performing a Shelving experiment, should not affect fit. Then set the parameter
        # in parametervault to the fitted center
        try:
            ampl_guess = max(return_counts[2:])
            self.fit_guess = [25, 30, ampl_guess, 0.0]

            # noinspection PyTupleAssignmentBalance
            popt, pcov = curve_fit(
                self.lorentzian_fit,
                return_detuning[2:],
                return_counts[2:],
                p0=self.fit_guess,
            )
            self.pv.set_parameter(
                ("Transitions", "main_cooling_369", U(popt[0], "MHz"))
            )
        except RuntimeError:
            return np.zeros(4), np.zeros([4, 4])
        return popt, pcov

    def program_pulser(self, freq, detuning):
        self.p["DipoleInterrogation.frequency"] = freq
        pulse_sequence = InterleavedPoint(self.p)
        pulse_sequence.program_sequence(self.pulser)
        self.pulser.start_number(int(self.p["InterleavedLinescan.repititions"]))
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        time_tags = self.pulser.get_timetags()
        counts = len(time_tags)
        self.pulser.reset_timetags()
        self.dv.add(detuning, counts)
        return detuning, counts

    def lorentzian_fit(self, detuning, center, fwhm, scale, offset):
        return offset + scale * 0.5 * fwhm / (
            (detuning - center) ** 2 + (0.5 * fwhm) ** 2
        )

    def finalize(self, cxn, context):
        pass


if __name__ == "__main__":
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = InterleavedLinescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
