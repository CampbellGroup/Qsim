import labrad
from labrad.units import WithUnit as U
import time
import numpy as np
from labrad.units import WithUnit
from common.lib.servers.abstractservers.script_scanner.scan_methods \
    import experiment


class DDSSweep(experiment):
    """
    Scan the 369 laser with the AOM double pass.
    """

    name = 'DDS Sweep'

    pv_sweep_dir = 'dds_sweep'
    exp_parameters = []
    exp_parameters.append((pv_sweep_dir, 'scan_frequency'))
    exp_parameters.append((pv_sweep_dir, 'scan_speed'))
    exp_parameters.append((pv_sweep_dir, 'repitition'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):
        self.p = self.parameters
        self.ident = ident

        self.cxn = labrad.connect(name='Wavemeter Line Scan')
        self.pulser = self.cxn.pulser
        self.dds_channel = 'repump'

    def run(self, cxn, context):
        self._set_frequency_values()
        rep = self.p.dds_sweep.repitition
        scan_speed = self.p.dds_sweep.scan_speed
        self.repititions = int(rep)
        self.pulser.new_sequence()
        for i, frequency in enumerate(self.frequency_values):
            self.pulser.add_dds_pulses([('repump', (i + 1)*scan_speed, scan_speed, U(frequency, 'MHz'),
                                         U(-5.0,'dBm'), U(0.0, 'deg'), U(0.0, 'Hz'),U(0.0, 'dB'))])
        self.pulser.program_sequence()
        self.pulser.start_number(self.repititions)

    def _set_frequency_values(self):
        frequency_scan = self.p.dds_sweep.scan_frequency
        min_freq = frequency_scan[0]['MHz']
        max_freq = frequency_scan[1]['MHz']
        self.steps = int(frequency_scan[2])
        self.frequency_values = np.linspace(min_freq, max_freq, self.steps)

    def _get_initial_dds_frequency(self):
        self._initial_frequency = self.pulser.frequency(self.dds_channel)

    def _set_dds_to_initial_frequency(self):
        self.pulser.frequency(self.dds_channel, self._initial_frequency)

    def finalize(self, cxn, context):
        self.cxn.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DDSSweep(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
