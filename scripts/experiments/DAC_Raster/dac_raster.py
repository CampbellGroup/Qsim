"""
### BEGIN EXPERIMENT INFO
[info]
name = dacRaster
load_into_scriptscanner = True
allow_concurrent = []
### END EXPERIMENT INFO
"""

import time

import labrad
from twisted.internet.defer import inlineCallbacks

from Qsim.scripts.experiments.Interleaved_Linescan.interleaved_linescan import (
    InterleavedLinescan,
)
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from config.dac_ad660_config import HardwareConfiguration as HC
from config.dac_ad660_config import MultipoleConfiguration as MC



class DACRaster(QsimExperiment):
    """
    This experiment will scan through a user specified list of DAC voltages and can be run when
    first trying to load the trap, or if the loadable position in the trap has been lost.
    """

    name = "DAC Raster"

    exp_parameters = []
    exp_parameters.append(("dacraster", "multipole"))
    exp_parameters.append(("dacraster", "multipole2"))
    exp_parameters.append(("dacraster", "scan"))
    exp_parameters.append(("dacraster", "scan2"))
    exp_parameters.append(("dacraster", "Delay_After_DAC_Change"))
    exp_parameters.extend(InterleavedLinescan.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.linescan = self.make_experiment(InterleavedLinescan)
        self.linescan_context = self.dv.context()
        self.linescan.initialize(cxn, self.linescan_context, ident)

        self.dac_server = self.cxn.dac_ad660_server  # connect to DAC server
        self.multipole_server = self.cxn.multipole_server
        self.dac_channels = HC.dac_channels
        self.electrodes = {}
        self.setup_datavault()

        for i, channel in enumerate(self.dac_channels):
            self.electrodes[channel.name] = channel.dac_channel_number

        self.mp1_values = self.get_scan_list(self.p["dacraster.scan"], None)
        if self.p["dacraster.multipole2"] != "None":
            self.mp2_values = self.get_scan_list(self.p["dacraster.scan2"], None)
        else:
            self.mp2_values = [1, ]

        self.total_step = len(self.mp1_values) * len(self.mp2_values)

    def run(self, cxn, context):

        step_count = 0

        if self.p["dacraster.multipole2"] != "None":
            for mp2 in self.mp2_values:
                self.update_multipole(mp2, self.p["dacraster.multipole2"])

                for mp1 in self.mp1_values:
                    step_count += 1
                    progress = step_count / self.total_step
                    self.update_multipole(mp1, self.p["dacraster.multipole"])

                    time.sleep(self.p["dacraster.Delay_After_DAC_Change"]["s"])
                    should_break = self.take_data(
                        progress,
                        cxn,
                        voltages=self.multipole_server.get_multipoles(),
                    )
                    if should_break:
                        return True
        else:
            for mp1 in self.mp1_values:
                step_count += 1
                progress = step_count / self.total_step
                self.update_multipole(mp1, self.p["dacraster.multipole"])

                time.sleep(self.p["dacraster.Delay_After_DAC_Change"]["s"])
                should_break = self.take_data(
                    progress,
                    cxn,
                    voltages=self.multipole_server.get_multipoles(),
                )
                if should_break:
                    return True

    def take_data(self, progress, cxn, voltages):
        should_break = self.update_progress(progress)
        if should_break:
            return True
        (center, fwhm, scale, offset), _ = self.linescan.run(cxn, self.linescan_context)
        multipoles = self.multipole_server.get_multipoles()

        self.dv.add(*multipoles, fwhm, context=self.context)

        # counts = self.pmt.get_next_counts('ON', int(self.p['dacraster.PMT_counts_to_average']), True)
        # self.data.append([current_dac_voltages, counts])

    def setup_datavault(self):
        """
        Adds parameters to datavault and parameter vault
        """
        self.dv.cd(["", self.name], True)
        self.dataset = self.dv.new(
            self.name,
            [(m.name, "num") for m in MC.multipoles],
            [("fwhm", "", "num")],
            context=self.context,
        )
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.context)
        return self.dataset

    @inlineCallbacks
    def update_dac(self, voltage, dac_num):
        yield self.dac_server.set_individual_analog_voltages([(dac_num, voltage)])

    @inlineCallbacks
    def update_multipole(self, value, multipole_name):
        yield self.multipole_server.set_multipole_by_name(multipole_name, value)


if __name__ == "__main__":
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DACRaster(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
