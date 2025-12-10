"""
### BEGIN EXPERIMENT INFO
[info]
name = 411_tweak_up
load_into_scriptscanner = True
allow_concurrent = []
### END EXPERIMENT INFO
"""

import labrad
import numpy as np
from Qsim.scripts.pulse_sequences.shelving_point import ShelvingPoint as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U


class Linescan411(QsimExperiment):
    """
    Measure 411nm shelving rate to the F7/2. Center of the linescan is dds defaults for 411.
    """

    name = "411 Linescan"

    exp_parameters = []
    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.append(("411_linescan", "line_scan"))

    exp_parameters.append(("ShelvingStateDetection", "repetitions"))
    exp_parameters.append(("ShelvingStateDetection", "state_readout_threshold"))
    exp_parameters.append(("Shelving_Doppler_Cooling", "doppler_counts_threshold"))
    exp_parameters.append(("Pi_times", "qubit_0"))
    exp_parameters.remove(("MicrowaveInterrogation", "detuning"))
    exp_parameters.remove(("MicrowaveInterrogation", "duration"))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):
        self.setup_datavault(
            "frequency", "probability"
        )  # gives the x and y names to Data Vault
        self.setup_grapher("411 Linescan")
        self.freqs = self.get_scan_list(self.p["411_linescan.line_scan"], "MHz")
        self.p["MicrowaveInterrogation.duration"] = self.p["Pi_times.qubit_0"]
        self.p["MicrowaveInterrogation.detuning"] = U(0.0, "kHz")
        self.p["Modes.state_detection_mode"] = "Shelving"
        for i, AOM_freq in enumerate(self.freqs):
            should_break = self.update_progress(i / float(len(self.freqs)))
            if should_break:
                break
            self.p["Transitions.shelving_411"] = U(AOM_freq, "MHz")
            self.program_pulser(sequence)
            [doppler_counts, detection_counts] = self.run_sequence(num=2, max_runs=500)
            # deshelving_errors = np.where(doppler_counts <= self.p["Shelving_Doppler_Cooling.doppler_counts_threshold"])
            # detection_counts = np.delete(detection_counts, deshelving_errors)
            hist = self.process_data(detection_counts)
            self.plot_hist(hist, folder_name="Shelving_Histogram")
            pop = self.get_pop(detection_counts)
            detuning = (AOM_freq - self.p["ddsDefaults.DP1_411_freq"]["MHz"]) * 2.0
            self.dv.add(detuning, pop)

    def finalize(self, cxn, context):
        pass


if __name__ == "__main__":
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ShelvingRate(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)


# Old method AOM scan over 10ish seconds

# """
# ### BEGIN EXPERIMENT INFO
# [info]
# name = 411_tweak_up
# load_into_scriptscanner = True
# allow_concurrent = []
# ### END EXPERIMENT INFO
# """
#
# import time
#
# import labrad
# from twisted.internet.defer import inlineCallbacks
# from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
# import numpy as np
# from labrad.units import WithUnit as U
# from Qsim.scripts.pulse_sequences.interleaved_point import InterleavedPoint
#
#
# class Linescan411(QsimExperiment):
#     """
#     THIS EXPERIMENT REQUIRES THE 411 DP AND 760S ON AND 411 SHUTTER OPEN BEFORE STARTING. LOWER 760 POWER FOR SUFFICIENT
#     DARK COUNTS.
#     This chanes the 411 AOM frequency according to "line_scan" and then averages PMT counts over "interogation_time".
#     """
#
#     name = "411 Linescan"
#
#     exp_parameters = []
#     exp_parameters.append(("411_linescan", "interogation_time"))
#     exp_parameters.append(("411_linescan", "center_AOM_freq"))
#     exp_parameters.append(("411_linescan", "line_scan"))
#
#     def initialize(self, cxn, context, ident):
#         self.ident = ident
#         self.reg = cxn.registry
#         self.pulser = cxn.pulser
#         self.reg.cd(["", "settings"])
#         self.init_AOM_freq = self.pulser.frequency('411DP1')
#         #self.AOM_power_transfer = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.368200836820084e-05, 0.0006694560669456067, 0.001422594142259414, 0.002343096234309623, 0.0034309623430962342, 0.004769874476987447, 0.005857740585774059, 0.007238493723849371, 0.007949790794979079, 0.008786610878661089, 0.008786610878661089, 0.008368200836820083, 0.007949790794979079, 0.0066945606694560665, 0.005857740585774059, 0.004602510460251045, 0.003765690376569037, 0.0029288702928870294, 0.0020920502092050207, 0.0012552301255230125, 0.0008368200836820083, 0.0006276150627615063, 0.00041841004184100416, 0.0004602510460251046, 0.0009205020920502092, 0.0020920502092050207, 0.004602510460251045, 0.00920502092050209, 0.017991631799163178, 0.03347280334728033, 0.05564853556485356, 0.08786610878661087, 0.1297071129707113, 0.18410041841004182, 0.25523012552301255, 0.3305439330543933, 0.4142259414225941, 0.5083682008368201, 0.5983263598326359, 0.6945606694560669, 0.7782426778242678, 0.8535564853556485, 0.9163179916317991, 0.9581589958158996, 0.9874476987447698, 1.0, 0.9874476987447698, 0.9497907949790795, 0.8912133891213389, 0.811715481171548, 0.7112970711297071, 0.6234309623430963, 0.5271966527196652, 0.4309623430962343, 0.3598326359832636, 0.27615062761506276, 0.20502092050209203, 0.15481171548117154, 0.11297071129707113, 0.0794979079497908, 0.058577405857740586, 0.0397489539748954, 0.025104602510460247, 0.016736401673640166, 0.0100418410041841, 0.005439330543933054, 0.0020920502092050207, 0.00041841004184100416, 0.0, 0.0, 0.0, 0.0, 0.00041841004184100416, 0.0008368200836820083, 0.0008368200836820083, 0.0006276150627615063, 0.00041841004184100416, 4.184100418410042e-05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#         #self.detunings = np.arange(-50, 51)
#
#     def run(self, cxn, context):
#         self.setup_datavault(
#             "frequency", "photons"
#         )  # gives the x and y names to Data Vault
#         self.setup_grapher("411 Linescan")
#         self.freqs = self.get_scan_list(
#             self.p["411_linescan.line_scan"], "MHz"
#         )
#         for i, freq in enumerate(self.freqs):
#             progress = i/len(self.freqs)
#             self.update_freq(U(freq, "MHz")+self.p["411_linescan.center_AOM_freq"], '411DP1')
#             should_break = self.take_data(progress, self.p["411_linescan.interogation_time"]["s"])
#             if should_break:
#                 self.update_freq(self.init_AOM_freq, '411DP1')
#                 return should_break
#
#     def take_data(self, progress, delay):
#         init_time = time.time()
#         currentfreq = self.pulser.frequency('411DP1')
#         counts = []
#         while (time.time() - init_time) < delay:
#             should_break = self.update_progress(progress)
#             counts.append(self.pmt.get_next_counts("ON", 1, False)[0])
#             if should_break:
#                 self.dv.add([currentfreq["MHz"], np.average(counts)])
#                 self.update_freq(self.init_AOM_freq, '411DP1')
#                 return True
#         self.dv.add([currentfreq["MHz"], np.average(np.asarray(counts))])
#         #interpolated_power_transfer = np.interp(currentfreq["MHz"]-450.0, self.detunings, self.AOM_power_transfer)
#         #self.dv.add([currentfreq["MHz"], np.average(np.asarray(counts))/interpolated_power_transfer])
#
#     @inlineCallbacks
#     def update_freq(self, freq, name='411DP1'):
#         yield self.pulser.frequency(name, freq)
