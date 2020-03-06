import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np
from Qsim.scripts.pulse_sequences.sub_sequences.AOM_timing import AOM_fitting as sequence


class AOM_fitting(QsimExperiment):

    name = 'AOM Fitting'

    '''
    Turns AOM on and timetags scatter then plots scatter as histogram
    '''

    exp_parameters = []
    exp_parameters.append(('AOMTiming', 'AOM'))
    exp_parameters.append(('AOMTiming', 'duration'))
    exp_parameters.append(('AOMTiming', 'frequency'))
    exp_parameters.append(('AOMTiming', 'power'))
    exp_parameters.append(('AOMTiming', 'repititions'))
    exp_parameters.extend(sequence.all_required_parameters())
    def initialize(self, cxn, context, ident):

        self.ident = ident

    def run(self, cxn, context):

        timetags = []
        repititions = self.p.AOMTiming.repititions
        self.program_pulser(sequence)
        for i in range(int(repititions)):
            self.pulser.reset_timetags()
            self.pulser.start_number(100)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            temp_timetags = self.pulser.get_timetags()
            timetags += list(temp_timetags)
            should_break = self.update_progress(i/float(repititions))
            if should_break:
                break
        self.dv.cd(['', 'AOMTiming'], True)
        self.dataset_hist = self.dv.new('AOMTiming',
                                        [('run', 'arb u')],
                                        [('Counts', 'Counts', 'num')])
        times = np.linspace(0, int(self.p.AOMTiming.duration['ns']) + 10000, 1000)
        y = np.histogram(np.array(timetags)*1e9, bins=times)[0]
        hist = np.column_stack((times[:-1], y))
        self.dv.add(hist)
        self.grapher.plot(self.dataset_hist, 'AOM Timing', False)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = AOM_fitting(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
