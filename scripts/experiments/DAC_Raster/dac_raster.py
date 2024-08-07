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
from config.dac_ad660_config import HardwareConfiguration as HC
from twisted.internet.defer import inlineCallbacks
import time
import numpy as np


class Electrode:
    def __init__(self, dac, minval, maxval, name=None):
        self.dac = str(dac).zfill(2)
        self.minval = minval
        self.maxval = maxval
        if name:
            self.name = name
        else:
            self.name = str('DAC: ' + str(dac))


class DACRaster(QsimExperiment):
    """
    This experiment will scan through a user specified list of DAC voltages and can be run when
    first trying to load the trap, or if the loadable position in the trap has been lost.
"""
    name = 'DAC Raster'

    exp_parameters = []
    exp_parameters.append(('dacraster', 'RF1_scan'))
    exp_parameters.append(('dacraster', 'RF2_scan'))
    exp_parameters.append(('dacraster', 'DC1_scan'))
    exp_parameters.append(('dacraster', 'DC2_scan'))
    exp_parameters.append(('dacraster', 'Delay_After_DAC_Change'))
    exp_parameters.append(('dacraster', 'PMT_counts_to_average'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.DACs = self.cxn.dac_ad660_server #connect to DAC server
        self.elec_dict = HC.elec_dict
        self.data = []
        self.electrodes = {}

        for i, (key, channel) in enumerate(self.elec_dict.items()):
            electrode = Electrode(channel.dac_channel_number,
                                  channel.allowed_voltage_range[0],
                                  channel.allowed_voltage_range[1],
                                  name=channel.name)
            self.electrodes[electrode.name] = electrode

        self.RF1_values = self.get_scan_list(self.p['dacraster.RF1_scan'], 'V')
        self.RF2_values = self.get_scan_list(self.p['dacraster.RF2_scan'], 'V')
        self.DC1_values = self.get_scan_list(self.p['dacraster.DC1_scan'], 'V')
        self.DC2_values = self.get_scan_list(self.p['dacraster.DC2_scan'], 'V')

        self.total_step = (len(self.RF1_values)) * (len(self.RF2_values)) * (len(self.DC1_values)) * (len(self.DC2_values))

    def run(self, cxn, context):

        step_count = 0

        for RF1_voltage in self.RF1_values:
            self.update_dac(RF1_voltage, self.electrodes['RF Rod 1'])

            for RF2_voltage in self.RF2_values:
                self.update_dac(RF2_voltage, self.electrodes['RF Rod 2'])

                for DC1_voltage in self.DC1_values:
                    self.update_dac(DC1_voltage, self.electrodes['DC Rod 1'])

                    for i, DC2_voltage in enumerate(self.DC2_values):
                        step_count += 1
                        progress = step_count / self.total_step
#                        should_break = self.update_progress(progress)
#                        if should_break:
#                            return should_break

                        self.update_dac(DC2_voltage, self.electrodes['DC Rod 2'])

                        time.sleep(self.p['dacraster.Delay_After_DAC_Change']['s'])
                        self.take_data(progress)


    def take_data(self, progress):

        should_break = self.update_progress(progress)
        if should_break:
            self.dv.add(self.data)
            return True
        counts = self.pmt.get_next_counts('ON', int(self.p['dacraster.PMT_counts_to_average']), True)
        current_DAC_voltages = self.DACs.get_analog_voltages()
        self.data.append([current_DAC_voltages, counts])


    @inlineCallbacks
    def update_dac(self, voltage, electrode):
        yield self.DACs.set_individual_analog_voltages([(electrode.dac, voltage)])

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DACRaster(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
