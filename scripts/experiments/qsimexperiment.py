from common.lib.servers.script_scanner.scan_methods import experiment
import numpy as np
import time


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
        self.hist_ctx = self.cxn.data_vault.context()
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
            error_message = error + '\n' + "Pulser is not running"
            raise KeyError(error_message)

        try:
            self.grapher = self.cxn.servers['grapher']
        except KeyError as error:
            error_message = error + '\n' + "Grapher is not running"
            raise KeyError(error_message)

        # try:
        #    self.timeharp = self.cxn.servers['timeharpserver']
        # except KeyError as error:
        #    error_message = str(error) + '\n' + "TimeHarp is not running"
        #    raise KeyError(error_message)

    def setup_datavault(self, x_axis, y_axis):
        """
        Adds parameters to datavault and parameter vault
        """
        self.dv.cd(['', self.name], True)
        self.dataset = self.dv.new(self.name, [(x_axis, 'num')],
                                   [(y_axis, '', 'num')])
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter])
        return self.dataset

    def setup_grapher(self, tab):
        if self.grapher is None:
            print('grapher not running')
        self.grapher.plot(self.dataset, tab, False)

    def update_progress(self, progress):
        if progress >= 1.0:
            progress = 1.0
        elif progress <= 0.0:
            progress = 0.0

        should_stop = self.pause_or_stop()
        self.sc.script_set_progress(self.ident, 100*progress)
        return should_stop

    def get_scan_list(self, scan, units, shuffle=False):
        if units is None:
            minvalue = scan[0]
            maxvalue = scan[1]
        else:
            minvalue = scan[0][units]
            maxvalue = scan[1][units]

        num_steps = scan[2]
        scan_list = np.linspace(minvalue, maxvalue, num_steps)
        if shuffle:
            return np.random.shuffle(list(scan_list))
        return list(scan_list)

    def program_pulser(self, pulse_sequence):
        pulse_sequence = pulse_sequence(self.p)
        pulse_sequence.program_sequence(self.pulser)

    def run_sequence(self, max_runs=1000, num=1):

        # empty arrays to store photon counts and time tags
        counts = np.array([])
        tt = np.array([])

        # choose state detection method and number of repetitions
        self.state_detection_mode = self.p.Modes.state_detection_mode
        if self.state_detection_mode == 'Shelving':
            reps = self.p.ShelvingStateDetection.repetitions
        elif self.state_detection_mode == 'Standard':
            reps = self.p.StandardStateDetection.repetitions
        elif self.state_detection_mode == 'StandardFiberEOM':
            reps = self.p.StandardStateDetection.repetitions
        else:
            return

        # program pulser for a given number of runs of the experiment, and collect readout counts
        for i in range(int(reps)/max_runs):
            self.pulser.start_number(max_runs)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            counts = np.concatenate((counts, self.pulser.get_readout_counts()))
            self.pulser.reset_readout_counts()
            self.pulser.reset_timetags()

        if int(reps) % max_runs != 0:
            runs = int(reps) % max_runs
            self.pulser.start_number(runs)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            counts = np.concatenate((counts, self.pulser.get_readout_counts()))
            self.pulser.reset_readout_counts()
            self.pulser.reset_timetags()

        # parse the photon counts for each call of ReadoutCount
        counts_parsed = []
        for i in range(num):
            counts_parsed.append(counts[i::num])
        return counts_parsed

    def run_sequence_with_timetags(self, max_runs=1000, num=1):
        # empty arrays to store photon counts and time tags
        counts = np.array([])
        tt = np.array([])

        # choose state detection method and number of repetitions
        self.state_detection_mode = self.p.Modes.state_detection_mode
        if self.state_detection_mode == 'Shelving':
            reps = self.p.ShelvingStateDetection.repetitions
        elif self.state_detection_mode == 'Standard':
            reps = self.p.StandardStateDetection.repetitions
        else:
            return

        for i in range(int(reps) / max_runs):
            self.pulser.start_number(max_runs)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            counts = np.concatenate((counts, self.pulser.get_readout_counts()))
            tt = np.concatenate((tt, self.pulser.get_timetags()))
            self.pulser.reset_readout_counts()
            self.pulser.reset_timetags()

        if int(reps) % max_runs != 0:
            runs = int(reps) % max_runs
            self.pulser.start_number(runs)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            counts = np.concatenate((counts, self.pulser.get_readout_counts()))
            tt = np.concatenate((tt, self.pulser.get_timetags()))
            self.pulser.reset_readout_counts()
            self.pulser.reset_timetags()

        # parse the photon counts for each call of ReadoutCount
        counts_parsed = []
        for i in range(num):
            counts_parsed.append(counts[i::num])
        return counts_parsed, [tt]

    def process_data(self, counts):
        bins = list(np.arange(0, np.max(counts) + 1, 1))
        events = [list(counts).count(i) for i in bins]
        hist = np.column_stack((bins, events))
        return hist

    def get_pop(self, counts):
        self.state_detection_mode = self.p.Modes.state_detection_mode
        if self.state_detection_mode == 'Shelving':
            threshold = self.p.ShelvingStateDetection.state_readout_threshold
        elif self.state_detection_mode == 'Standard':
            threshold = self.p.StandardStateDetection.state_readout_threshold
        elif self.state_detection_mode == 'StandardFiberEOM':
            threshold = self.p.StandardStateDetection.state_readout_threshold
        else:
            return
        prob = float(len(np.where(counts >= threshold)[0]))/float(len(counts))
        return prob

    def plot_hist(self, hist, folder_name='Histograms', create_new=True):
        self.dv.cd(['', folder_name], True, context=self.hist_ctx)
        if create_new:
            self.dataset_hist = self.dv.new(folder_name, [('run', 'arb u')],
                                            [('Counts', 'Counts', 'num')], context=self.hist_ctx)
        self.dv.add(hist, context=self.hist_ctx)
        if create_new:
            self.grapher.plot(self.dataset_hist, 'Histogram', False)

    def get_timeharp_timetags(self, measure_time, buffer_size=131072):
        self.timeharp.start_measure(measure_time)
        time.sleep(measure_time/1000.)
        data = self.timeharp.read_fifo(buffer_size)
        stamps = data[0]
        data_length = data[1]
        stamps = stamps[0:data_length]
        timetags = self.convert_timetags(stamps)
        while data_length > 0:
            data = self.timeharp.read_fifo(buffer_size)
            stamps = data[0]
            data_length = data[1]
            stamps = stamps[0:data_length]
            timetags += self.convert_timetags(stamps)
        self.timeharp.stop_measure()
        return timetags

    def convert_timetags(self, data):
        timetags = []
        for i, stamp in enumerate(data):
            timetag = (stamp >> 10) & 2 ** 15 - 1
            timetag = (stamp >> 10) & (2 ** 15 - 1)
            timetag = timetag * 25. / 1000.  # time in nanoseconds
            if timetag != 0:
                timetags.append(timetag)
        return timetags

    def _finalize(self, cxn, context):
        self.pmt.set_mode(self.init_mode)
        self.finalize(cxn, context)
        self.sc.finish_confirmed(self.ident)
