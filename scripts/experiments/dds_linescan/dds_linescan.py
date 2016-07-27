import labrad
import time
import numpy as np
from labrad.units import WithUnit
from common.lib.servers.abstractservers.script_scanner.scan_methods \
    import experiment


class DDSLinescan(experiment):
    """
    Scan the 369 laser with the AOM double pass.
    """

    name = 'DDS Line Scan'

    pv_linescan_dir = 'dds_linescan'
    pv_dds_dir = 'dds'
    exp_parameters = []
    exp_parameters.append((pv_dds_dir, 'cooling_amplitude'))
    exp_parameters.append((pv_linescan_dir, 'cooling_frequency'))
    exp_parameters.append((pv_linescan_dir, 'scan_speed'))


    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):
        self.p = self.parameters
        self.ident = ident

        self.cxn = labrad.connect(name='Wavemeter Line Scan')
        self.dv = self.cxn.data_vault
        self.grapher = self.cxn.grapher
        self.pmt = self.cxn.normalpmtflow
        self.pulser = self.cxn.pulser

    def run(self, cxn, context):
        self._data_vault_and_grapher_setup()
        self._set_frequency_values()

        tempdata = []
        for kk, frequency in enumerate(self.frequency_values):
            if self.pause_or_stop():
                break

            self._set_dds_frequency(frequency, context)
            # Wait for frequency to be set.
            time.sleep(self.scan_speed)

            counts = self.pmt.get_next_counts('ON', 1, False)
            self.dv.add([frequency, counts])

            progress = 100*float(kk)/self.steps
            self.sc.script_set_progress(self.ident, progress)

    def _set_dds_frequency(self, frequency, context):
        """
        Change the frequency on the 369 DDS pulser channel to frequency where
        frequency is in MHz.
        """
        unitful_frequency = WithUnit(frequency, 'MHz')
        self.pulser.frequency('369', unitful_frequency, context=context)

    def _set_frequency_values(self):
        frequency_scan = self.p.dds_linescan.cooling_frequency
        min_freq = frequency_scan[0]['MHz']
        max_freq = frequency_scan[1]['MHz']
        self.steps = int(frequency_scan[2])
        self.frequency_values = np.linspace(min_freq, max_freq, self.steps)

    def _data_vault_and_grapher_setup(self):
        self.dv.cd('dds_linescan', True)
        dataset = self.dv.new('dds_line_scan', [('freq', 'Hz')],
                              [('', 'Amplitude', 'kilocounts/sec')])

        self.grapher.plot(dataset, 'spectrum', False)

        amplitude = self.p.dds.cooling_amplitude
        self.dv.add_parameter('cooling_amplitude', amplitude)
        self.scan_speed = self.p.dds_linescan.scan_speed
        self.dv.add_parameter('scan_speed', self.scan_speed)

    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DDSLinescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
