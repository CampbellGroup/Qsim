import labrad
from Qsim.scripts.pulse_sequences.microwave_point import microwave_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class MicrowaveRabiFlopping(QsimExperiment):
    """
    repeatedly prepare the |0> state, interrogate with resonant microwaves for
    a variable time t and measure the population in the bright state
    """

    name = 'Microwave Rabi Flopping'

    exp_parameters = []
    exp_parameters.append(('RabiFlopping', 'scan'))
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))

    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.append(('MicrowaveInterrogation', 'AC_line_trigger'))

    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('MicrowaveInterrogation', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.pzt_server = cxn.piezo_server
        self.cavity_chan = 1
        self.cavity_voltage = 0.0
        self.counts_track_mean = 0.0

    def run(self, cxn, context):

        self.cavity_voltage = self.pzt_server.get_voltage(self.cavity_chan)
        print(self.cavity_voltage)
        qubit = self.p.Line_Selection.qubit
        mode = self.p.Modes.state_detection_mode

        init_bright_state_pumping_method = self.p.BrightStatePumping.method
        init_microwave_pulse_sequence = self.p.MicrowaveInterrogation.pulse_sequence
        init_optical_pumping_method = self.p.OpticalPumping.method

        self.p['BrightStatePumping.method'] = 'Microwave'
        #self.p['MicrowaveInterogation.pulse_sequence'] = 'standard'

        self.pulser.line_trigger_state(self.p.MicrowaveInterrogation.AC_line_trigger == 'On')

        self.setup_datavault('time', 'probability')  # gives the x and y names to Data Vault
        if mode == 'Shelving':
            self.setup_shelving_rabi_datavault()
        elif mode == 'Standard':
            self.setup_datavault('time', 'probability')
        self.setup_grapher('Rabi Flopping ' + qubit)

        self.times = self.get_scan_list(self.p.RabiFlopping.scan, 'us')

        for i, duration in enumerate(self.times):
            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                self.pulser.line_trigger_state(False)
                break
            self.p['MicrowaveInterrogation.duration'] = U(duration, 'us')

            if mode == 'Standard':
                # force standard optical pumping if standard readout method used
                # no sense in quadrupole optical pumping by accident if using standard readout
                self.p['OpticalPumping.method'] = 'Standard'

            self.program_pulser(sequence)
            if mode == 'Shelving':
                [doppler_counts, detection_counts] = self.run_sequence(max_runs=500, num=2)
                errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                counts = np.delete(detection_counts, errors)
                countsDopFixed = np.delete(doppler_counts, errors)
            elif mode == 'Standard':
                [counts] = self.run_sequence()
            else:
                print 'Detection mode not selected!!!'

            if i % self.p.StandardStateDetection.points_per_histogram == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist)

            pop = self.get_pop(counts)
            if mode == 'Shelving':
                self.dv.add(i, duration, pop, len(counts), context=self.shelving_context)
            else:
                self.dv.add(duration, pop)

            if mode == 'Shelving':
                if i == 1:
                    self.counts_track_mean = np.mean(countsDopFixed)
                    print('mean doppler counts on first experiment is  = ' + str(self.counts_track_mean))
                elif i > 1:
                    diff = np.mean(countsDopFixed) - self.counts_track_mean
                    if np.abs(diff) > 7.0:
                        self.cavity_voltage = self.cavity_voltage + np.sign(diff) * 0.005
                        if np.sign(diff)*0.005 < 0.2:
                            self.pzt_server.set_voltage(self.cavity_chan, U(self.cavity_voltage, 'V'))
                            print('Updated cavity voltage to ' + str(self.cavity_voltage) + ' V')
                    else:
                        pass

        # reset all the init settings that you forced for this experiment
        self.p['BrightStatePumping.method'] = init_bright_state_pumping_method
        self.p['MicrowaveInterrogation.pulse_sequence'] = init_microwave_pulse_sequence
        self.p['OpticalPumping.method'] = init_optical_pumping_method
        self.pulser.line_trigger_state(False)

    def setup_shelving_rabi_datavault(self):

        self.shelving_context = self.dv.context()
        self.dv.cd(['', 'rabi_flopping_shelving'], True, context=self.shelving_context)
        self.hf_dark_dataset = self.dv.new('counts', [('run', 'arb')],
                                           [('time', 'time', 'num'),
                                            ('prob', 'prob', 'num'),
                                            ('experiments', 'experiments', 'num')],
                                           context=self.shelving_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.shelving_context)

    def finalize(self, cxn, context):
        pass

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveRabiFlopping(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
