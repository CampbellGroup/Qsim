import labrad
from Qsim.scripts.pulse_sequences.shelving_point import shelving_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U

class ShelvingRate(QsimExperiment):
    """
    Measure 411nm shelving rate to the F7/2
    """

    name = 'ShelvingRate'

    exp_parameters = []
    exp_parameters.append(('ShelvingRate', 'scan'))
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.append(('StateDetection', 'state_readout_threshold'))
    exp_parameters.append(('StateDetection', 'points_per_histogram'))

    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('Shelving', 'duration'))


    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):
        self.setup_datavault('time', 'probability')
        self.setup_grapher('ShelvingRate')
        self.times = self.get_scan_list(self.p.ShelvingRate.scan, 'ms')
        for i, duration in enumerate(self.times):
            print duration
            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                break
            self.p['Shelving.duration'] = U(duration, 'ms')
            print self.p.items()
            self.program_pulser(sequence)
            counts = self.run_sequence()
            if i % self.p.StateDetection.points_per_histogram == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist)
            pop = self.get_pop(counts)
            self.dv.add(duration, pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ShelvingRate(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
