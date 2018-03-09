from common.lib.servers.script_scanner.scan_methods import experiment
import numpy as np


class QsimExperiment(experiment):

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def __init__(self, name=None, required_parameters=None, cxn=None,
                 min_progress=0.0, max_progress=100.0,):

        required_parameters = self.all_required_parameters()
        super(experiment, self).__init__(name, required_parameters)

        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name

        self.p = self.parameters
        self.cxn = cxn
        self.pv = None
        self.sc = None
        self.init_mode = self.cxn.NormalPMTFlow.getcurrentmode()
        self.cxn.NormalPMTFlow.set_mode('Normal')

    def _connect(self):
        experiment._connect(self)
        try:
            self.dv = self.cxn.servers['Data Vault']
        except KeyError as error:
            error_message = error + '\n' + "DataVault is not running"
            raise KeyError(error_message)

        try:
            self.pmt = self.cxn.servers['NormalPMTFlow']
        except KeyError as error:
            error_message = error + '\n' + "NormalPMTFlow is not running"
            raise KeyError(error_message)

        try:
            self.pulser = self.cxn.servers['pulser']
        except KeyError as error:
            error_message = error + '\n' + "DataVault is not running"
            raise KeyError(error_message)

        try:
            self.grapher = self.cxn.servers['grapher']
        except KeyError as error:
            error_message = error + '\n' + "Grapher is not running"
            raise KeyError(error_message)

    def setup_datavault(self, x_axis, y_axis):

        '''
        Adds parameters to datavault and parameter vault
        '''

        self.dv.cd(['', self.name], True)
        self.dataset = self.dv.new(self.name, [(x_axis, 'num')],
                                   [(y_axis, '', 'num')])

        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter])

        return self.dataset

    def setup_grapher(self, tab):
        if self.grapher is None:
            print 'grapher not running'
        self.grapher.plot(self.dataset, tab, False)

    def update_progress(self, progress):
            if progress >= 1.0:
                progress = 1.0
            elif progress <= 0.0:
                progress = 0.0

            should_stop = self.pause_or_stop()
            self.sc.script_set_progress(self.ident, 100*progress)
            return should_stop

    def get_scan_list(self, scan, units):
        if units is None:
            minvalue = scan[0]
            maxvalue = scan[1]
        else:
            minvalue = scan[0][units]
            maxvalue = scan[1][units]

        num_steps = scan[2]
        scan_list = np.linspace(minvalue, maxvalue, num_steps)
        return list(scan_list)

    def program_pulser(self, pulse_sequence):
        pulse_sequence = pulse_sequence(self.p)
        pulse_sequence.programSequence(self.pulser)

    def run_sequence(self, max_runs=1000):

        counts = np.array([])
        for i in range(int(self.p.StateDetection.repititions)/max_runs):
            self.pulser.start_number(max_runs)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            counts = np.concatenate((counts, self.pulser.get_readout_counts()))
            self.pulser.reset_readout_counts()
        if int(self.p.StateDetection.repititions) % max_runs is not 0:
            self.pulser.start_number(int(self.p.StateDetection.repititions) % max_runs)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            counts = np.concatenate((counts, self.pulser.get_readout_counts()))
            self.pulser.reset_readout_counts()
        print len(counts), 'length of counts'
        return counts

    def process_data(self, counts):

        repititions = len(counts)
        data = np.column_stack((np.arange(repititions),
                                counts))
        y = np.histogram(data[:, 1],
                         int(np.max([data[:, 1].max() - data[:, 1].min(), 1])))
        counts = y[0]
        bins = y[1][:-1]
        if bins[0] < 0:
            bins = bins + .5
        hist = np.column_stack((bins, counts))
        return hist

    def get_pop(self, counts):
        self.thresholdVal = self.p.StateDetection.state_readout_threshold
        prob = len(np.where(counts > self.thresholdVal)[0])/float(len(counts))
        return prob

    def _finalize(self, cxn, context):
        self.pmt.set_mode(self.init_mode)
        self.finalize(cxn, context)
        self.sc.finish_confirmed(self.ident)
