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


class DACRaster(QsimExperiment):
    """
    This experiment will scan through a user specified list of DAC voltages and can be run when
    first trying to load the trap, or if the loadable position in the trap has been lost.
    """

    name = "DAC Raster"

    exp_parameters = []
    exp_parameters.append(("dacraster", "RF1_scan"))
    exp_parameters.append(("dacraster", "DC1_scan"))
    exp_parameters.append(("dacraster", "Delay_After_DAC_Change"))
    exp_parameters.append(("dacraster", "PMT_counts_to_average"))
    exp_parameters.extend(InterleavedLinescan.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.linescan = self.make_experiment(InterleavedLinescan)
        self.linescan_context = self.dv.context()
        self.linescan.initialize(cxn, self.linescan_context, ident)
        self.DACs = self.cxn.dac_ad660_server  # connect to DAC server
        self.dac_channels = HC.dac_channels
        self.electrodes = {}
        self.setup_datavault()

        for i, channel in enumerate(self.dac_channels):
            self.electrodes[channel.name] = channel.dac_channel_number

        self.RF_values = self.get_scan_list(self.p["dacraster.RF1_scan"], "V")
        self.DC_values = self.get_scan_list(self.p["dacraster.DC1_scan"], "V")

        self.total_step = len(self.RF_values) * len(self.DC_values)

    def run(self, cxn, context):

        step_count = 0

        for RF_voltage in self.RF_values:
            self.update_dac(RF_voltage / 2, self.electrodes["RF Rod 1"])
            self.update_dac(-RF_voltage / 2, self.electrodes["RF Rod 2"])

            for DC_voltage in self.DC_values:
                step_count += 1
                progress = step_count / self.total_step
                self.update_dac(DC_voltage / 2, self.electrodes["DC Rod 1"])
                self.update_dac(-DC_voltage / 2, self.electrodes["DC Rod 2"])

                time.sleep(self.p["dacraster.Delay_After_DAC_Change"]["s"])
                should_break = self.take_data(
                    progress,
                    cxn,
                    (RF_voltage / 2, DC_voltage / 2, -DC_voltage / 2, -RF_voltage / 2),
                )
                if should_break:
                    return True

    def take_data(self, progress, cxn, voltages):
        should_break = self.update_progress(progress)
        if should_break:
            return True
        (center, fwhm, scale, offset), _ = self.linescan.run(cxn, self.linescan_context)
        current_dac_voltages = [v[1] for v in self.DACs.get_current_voltages()][4:]

        self.dv.add(*current_dac_voltages, fwhm, context=self.context)

        # counts = self.pmt.get_next_counts('ON', int(self.p['dacraster.PMT_counts_to_average']), True)
        # self.data.append([current_dac_voltages, counts])

    def setup_datavault(self):
        """
        Adds parameters to datavault and parameter vault
        """
        self.dv.cd(["", self.name], True)
        self.dataset = self.dv.new(
            self.name,
            [("RF1", "num"), ("DC1", "num"), ("DC2", "num"), ("RF2", "num")],
            [("fwhm", "", "num")],
            context=self.context,
        )
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.context)
        return self.dataset

    @inlineCallbacks
    def update_dac(self, voltage, dac_num):
        yield self.DACs.set_individual_analog_voltages([(dac_num, voltage)])


if __name__ == "__main__":
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DACRaster(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
