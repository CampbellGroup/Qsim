import labrad
import time
import numpy as np
from labrad.units import WithUnit
from Qsim.scripts.pulse_sequences.sub_sequences.DipoleInterogation import dipole_interogation as sequence
from Qsim.scripts.pulse_sequences.sub_sequences.DopplerCooling import doppler_cooling
from common.lib.servers.abstractservers.script_scanner.scan_methods \
    import experiment


class InterleavedLinescan(experiment):
    """
    Scan the 369 laser with the AOM double pass interleaved with doppler cooling.
    """

    name = 'Interleaved Line Scan'

    required_parameters = [
                           ('InterleavedLinescan', 'doppler_cooling_time'),
                           ('InterleavedLinescan', 'interogation_repititions'),
                           ('InterleavedLinescan', 'line_scan'),
    ]

    required_parameters.extend(sequence.all_required_parameters())
    required_parameters.remove(('DipoleInterogation', 'interogation_frequency'))

    @classmethod
    def all_required_parameters(cls):
        return cls.required_parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident

        self.cxn = labrad.connect(name='Interleaved Line Scan')
        self.pulser = self.cxn.pulser
        self.dds_channel = '369'

    def run(self, cxn, context):
        min, max, steps = self.parameters.InterleavedLinescan.line_scan
        scan = np.linspace(min['MHz'], max['MHz'], steps)
        scan = [WithUnit(pt, 'MHz') for pt in scan]
        power = self.parameters.DipoleInterogation.interogation_power
        for freq in scan:
            print freq, power
            self.program_pulser(freq)

    def program_pulser(self, freq):
        self.pulser.reset_timetags()
        self.parameters['DipoleInterogation.interogation_frequency'] = freq
        pulse_sequence = sequence(self.parameters)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_single()
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        #timetags = self.pulser.get_timetags()
        #if timetags.size >= 65535:
        #    raise Exception("Timetags Overflow, should reduce number of back to back pulse sequences")
        #else:
            #print 'save data'
            #self.dv.add([index, timetags.size], context = self.total_timetag_save_context)



    def finalize(self, cxn, context):
        self.cxn.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = InterleavedLinescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
