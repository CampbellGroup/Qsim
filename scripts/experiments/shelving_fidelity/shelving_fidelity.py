import labrad
from Qsim.scripts.pulse_sequences.shelving_fidelity import shelving_fidelity as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
#from Qsim.scripts.experiments.interleaved_linescan.interleaved_linescan import InterleavedLinescan
#from Qsim.scripts.experiments.shelving_411.shelving_411 import ShelvingRate
#from Qsim.scripts.experiments.Microwave_Ramsey_Experiment.microwave_ramsey_experiment import MicrowaveRamseyExperiment
from Qsim.scripts.pulse_sequences.bright_state_prepepration import bright_state_preperation
import numpy as np
from labrad.units import WithUnit as U


class shelving_fidelity(QsimExperiment):
    """
    shelving fidelity with experimental checks
    """

    name = 'Shelving Fidelity'

    exp_parameters = []
    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.append(('Pi_times', 'qubit_plus'))
    exp_parameters.append(('Pi_times', 'qubit_minus'))

    exp_parameters.append(('MicrowaveInterogation', 'repititions'))
    exp_parameters.append(('ShelvingStateDetection', 'repititions'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.append(('ShelvingStateDetection', 'sequence_iterations'))

    exp_parameters.append(('Timetags', 'save_timetags'))
    exp_parameters.append(('Timetags', 'lower_threshold'))
    exp_parameters.append(('Timetags', 'upper_threshold'))
    exp_parameters.append(('MicrowaveInterogation', 'AC_line_trigger'))
    exp_parameters.append(('MicrowaveInterogation', 'delay_from_line_trigger'))
    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('MicrowaveInterogation', 'detuning'))
    exp_parameters.remove(('MicrowaveInterogation', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        if self.p.MicrowaveInterogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterogation.delay_from_line_trigger)

        qubit = self.p.Line_Selection.qubit
        collect_timetags = self.p.Timetags.save_timetags
        if qubit == 'qubit_0':
            pi_time = self.p.Pi_times.qubit_0

        elif qubit == 'qubit_plus':
            pi_time = self.p.Pi_times.qubit_plus

        elif qubit == 'qubit_minus':
            pi_time = self.p.Pi_times.qubit_minus

        self.p['MicrowaveInterogation.duration'] = pi_time
        self.p['MicrowaveInterogation.detuning'] = U(0.0, 'kHz')
        self.p['Modes.state_detection_mode'] = 'Shelving'
        self.setup_prob_datavault()
        self.setup_timetags_datavault()
        self.program_pulser(sequence)

        i = 0
        while i < self.p.ShelvingStateDetection.sequence_iterations:
            i += 1
            should_break = self.update_progress(np.random.random())
            old_params = dict(self.p.iteritems())
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters
            if self.p != old_params:
                self.program_pulser(sequence)
            if collect_timetags == 'OFF':
                [counts_doppler_bright, counts_bright, counts_doppler_dark, counts_dark] = self.run_sequence(max_runs=250, num=4)
            elif collect_timetags == 'ON':
                [counts_doppler_bright, counts_bright, counts_doppler_dark, counts_dark], timetags = self.run_sequence_with_timetags(max_runs=150, num=4)
                ttBright = []
                [timetags_bright, timetags_dark] = self.process_timetags(timetags, counts_bright, counts_dark)
                save_timetags = np.where(np.logical_and(counts_bright >= self.p.Timetags.lower_threshold,
                                                        counts_bright <= self.p.Timetags.upper_threshold))
                #for location in save_timetags[0]:
                #    self.dv.add(counts_bright[location], np.array(timetags_bright[int(location)][0]), context=self.tt_context)

            padWidth = 1
            bright_errors = np.where(counts_doppler_bright <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            print('Bright doppler errors at' + str(bright_errors))
            bright_delete = np.array([])
            for error in bright_errors[0]:
                # we are going to delete the experiments 1 before and after the error for safety
                tempPad = range(error - padWidth, error + padWidth + 1, 1)
                bright_delete = np.concatenate((bright_delete, tempPad))
            bright_delete = bright_delete[(bright_delete < len(counts_doppler_bright)) & (bright_delete >= 0.0)]
            print('Bright padded doppler errors at' + str(bright_delete))
            counts_bright = np.delete(counts_bright, bright_delete)

            dark_errors = np.where(counts_doppler_dark <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            dark_delete = np.array([])
            for error in dark_errors[0]:
                # we are going to delete the experiments 1 before and after the error for safety
                tempPad = range(error - padWidth, error + padWidth + 1, 1)
                dark_delete = np.concatenate((dark_delete, tempPad))
            dark_delete = dark_delete[(dark_delete < len(counts_doppler_dark)) & (dark_delete >= 0.0)]
            counts_dark = np.delete(counts_dark, dark_delete)



            hist_bright = self.process_data(counts_bright)
            hist_dark = self.process_data(counts_dark)

            # this part plots the histograms on the hist panel in the shelving_fidelity tab
            self.plot_hist(hist_bright, folder_name='Shelving_Histogram')
            self.plot_hist(hist_dark, folder_name='Shelving_Histogram')

            #this processes the counts and calculates the fidelity and plots it on the bottom panel
            probDark, probBright = self.plot_prob(i, counts_bright, counts_dark)

            print 'Mean Doppler Counts:', np.mean(counts_doppler_bright)
            print('probDark = ' + str(probDark))
            print('probBright = ' + str(probBright))

            # this will do something if there was a dark state error
            if probDark != 0.0:
                self.pulser.line_trigger_state(False)
                self.pulser.stop_sequence()
                break

            #if i % self.p.ShelvingFidelity.drift_track_iterations == 0:
                #drift_context = self.sc.context()

                #init_sequence = self.p.MicrowaveInterogation.pulse_sequence
                #self.p.MicrowaveInterogation.pulse_sequence = 'standard'

                #self.linescan = self.make_experiment(InterleavedLinescan)
                #self.linescan.initialize(self.cxn, drift_context, self.ident)
                #self.linescan.run(self.cxn, drift_context)

                #self.shelving_rate = self.make_experiment(ShelvingRate)
                #self.shelving_rate.initialize(self.cxn, drift_context, self.ident)
                #self.shelving_rate.run(self.cxn, drift_context)

                #self.sc.pause_script(self.ident, True)
                #self.p.MicrowaveInterogation.pulse_sequence = init_sequence
                #self.program_pulser(sequence)

        # reset the line trigger and delay to false
        self.pulser.line_trigger_state(False)

    def setup_prob_datavault(self):
        self.dv_context = self.dv.context()
        self.dv.cd(['', 'shelving_fidelity'], True, context=self.dv_context)

        self.dataset_prob = self.dv.new('shelving_fidelity', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num'),
                                         ('Prob', 'contrast', 'num')], context=self.dv_context)
        self.grapher.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.dv_context)

    def setup_timetags_datavault(self):
        self.tt_context = self.dv.context()
        self.dv.cd(['', 'timetagged_errors'], True, context=self.tt_context)
        self.timetags_dataset = self.dv.new('timetagged_errors', [('counts_bright', 'num')],
                                            [('timetags', 'bright_timetag_errors', 'list')], context=self.tt_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_context)

    def plot_prob(self, num, counts_dark, counts_bright):
        print num
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(num, prob_dark, prob_bright,
                    prob_bright - prob_dark, context=self.dv_context)
        return prob_dark, prob_bright

    def process_timetags(self, timetags, counts_bright, counts_dark):
        # function should take in the timetags, and parse into a list of lists for the timetags
        # during each  state detection sequence
        ttBright = []
        ttDark = []
        tt = timetags
        for b, d in zip(counts_bright, counts_dark):
            tempBright = tt[:int(b)]
            tempDark = tt[int(b):int(d + b)]
            ttBright.append(tempBright)
            ttDark.append(tempDark)
            tt = tt[int(b + d):]
        return ttBright, ttDark

    def finalize(self, cxn, context):
        pass

    def check_pi_time(self, number_pi_pulses):
        pi_time_check_context = self.sc.context()
        init_sequence = self.p.MicrowaveInterogation.pulse_sequence
        self.p['MicrowaveInterogation.pulse_sequence'] = 'standard'
        self.p['MicrowaveInterogation.duration'] = pi_time*number_pi_pulses

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = shelving_fidelity(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
