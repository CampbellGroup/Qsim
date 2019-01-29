import labrad
from Qsim.scripts.pulse_sequences.interleaved_point import interleaved_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit
import numpy as np


class MM_reduction(QsimExperiment):

    name = 'MM Reduction'

    exp_parameters = []

    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))

    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.remove(('DipoleInterogation', 'frequency'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.reg = cxn.registry
        self.reg.cd(['', 'settings'])
        self.RF_freq = self.pulser.frequency('RF_Drive')

    def run(self, cxn, context):
        self.dv.cd(['', 'MM_reduction'], True)

        self.dataset = self.dv.new('MM_reduction', [('run', 'prob')],
                                        [('amp', 'carrier', 'num'),
                                         ('Prob', 'blue_sideband', 'num'),
                                         ('Prob', 'red_sideband', 'num')]) 

        self.setup_grapher('MM reduction')
        i = 0
        while True:
            i += 1
            should_break = self.update_progress(50)
            if should_break:
                return should_break
            freq1 = self.p.Transitions.main_cooling_369/2.0 + WithUnit(200.0, 'MHz')
            freq2 = self.p.Transitions.main_cooling_369/2.0 + WithUnit(200.0, 'MHz') + self.RF_freq/2
            freq3 = self.p.Transitions.main_cooling_369/2.0 + WithUnit(200.0, 'MHz') - self.RF_freq/2
            counts1 = self.program_pulser(freq1)
            counts2 = self.program_pulser(freq2)
            counts3 = self.program_pulser(freq3)
            self.dv.add(i, counts1, counts2, counts3)
            self.reload_all_parameters()
            self.p = self.parameters

    def program_pulser(self, freq):
        self.p['DipoleInterogation.frequency'] = freq
        pulse_sequence = sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_number(100)
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        time_tags = self.pulser.get_timetags()
        counts = len(time_tags)
        self.pulser.reset_timetags()
        return counts

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MM_reduction(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
