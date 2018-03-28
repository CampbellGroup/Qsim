import labrad
import numpy as np
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.pulse_sequences.bright_state_preperation import bright_state_preperation as sequence_bright
from Qsim.scripts.pulse_sequences.dark_state_preperation import dark_state_preperation as sequence_dark

__scriptscanner_name__ = 'Delaystagescan'  # this should match the class name


class Delaystagescan(QsimExperiment):

    name = 'Ramsey Delay Stage Scan'

    exp_parameters = []
    exp_parameters.append(('Delaystagescan', 'scan'))
    exp_parameters.append(('Delaystagescan', 'average'))
    exp_parameters.append(('Delaystagescan', 'mode'))
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('DopplerCooling', 'cooling_power'))
    exp_parameters.append(('Delaystagescan', 'ML_power'))
    exp_parameters.append(('Delaystagescan', 'state_prep'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.extend(sequence_bright.all_required_parameters())
    exp_parameters.extend(sequence_dark.all_required_parameters())

    exp_parameters.remove(('StateDetection', 'mode'))

    def initialize(self, cxn, context, ident):

        self.ident = ident

        self.chan = 2
        self.keithley = self.cxn.keithley_2230g_server
        self.keithley.select_device(0)

        self.init_ML_power = self.pulser.amplitude('ModeLockedSP')
        self.init_cooling_freq = self.pulser.frequency('369DP')
        self.init_cooling_power = self.pulser.amplitude('DopplerCoolingSP')
        self.p['StateDetection.mode'] = 'ML'

    def run(self, cxn, context):

        '''
        Main loop
        '''
        from labrad.units import WithUnit as U
        self.U = U
        self.state_prep = self.p.Delaystagescan.state_prep
        self.set_scannable_parameters()
        self.keithley.gpib_write('Apply CH1,' + str(self.init_volt) + 'V')
        self.keithley.output(self.chan, True)
        # this is real laser detuning
        self.pulser.frequency('369DP', self.cooling_center + self.detuning/2.0)
        self.pulser.amplitude('DopplerCoolingSP', self.cooling_power)
        self.pulser.amplitude('ModeLockedSP', self.ML_power)
        self.path = self.setup_datavault('Volts', 'kcounts/sec')
        self.setup_grapher('Ramsey Delay Stage Piezo Scan')

        try:
            MLfreq = cxn.bristol_521.get_wavelength()
            self.dv.add_parameter('Bristol Reading', MLfreq)
        except:
            pass

        if self.state_prep == 'OFF':
            if self.mode == 'DIFF':
                self.pmt.set_mode('Differential')
            else:
                self.pmt.set_mode('Normal')
            for i, volt in enumerate(self.x_values):
                should_break = self.update_progress(i/float(len(self.x_values)))
                if should_break:
                    break
                print volt
                # we write direct GPIB for speed
                self.keithley.gpib_write('APPLy CH2,' + str(volt) + 'V')
                counts = self.pmt.get_next_counts(self.mode, self.average, True)
                self.dv.add(volt, counts)
        elif self.state_prep == 'BRIGHT':
            self.pmt.set_mode('Normal')
            for i, volt in enumerate(self.x_values):
                should_break = self.update_progress(i / float(len(self.x_values)))
                if should_break:
                    break
                self.keithley.gpib_write('APPLy CH2,' + str(volt) + 'V')
                counts = self.program_pulser(sequence_bright)
                self.dv.add(volt, np.sum(np.array(counts))/self.p.StateDetection.repititions)
        else:
            for i, volt in enumerate(self.x_values):
                self.pmt.set_mode('Normal')
                should_break = self.update_progress(i / float(len(self.x_values)))
                if should_break:
                    break
                self.keithley.gpib_write('APPLy CH2,' + str(volt) + 'V')
                counts = self.program_pulser(sequence_dark)
                self.dv.add(volt, np.sum(np.array(counts))/self.p.StateDetection.repititions)

    def set_scannable_parameters(self):
        '''
        gets parameters, called in run so scan works
        '''

        self.cooling_power = self.p.DopplerCooling.cooling_power
        self.cooling_center = self.p.Transitions.main_cooling_369/2. + self.U(200.0, 'MHz')
        self.detuning = self.p.DopplerCooling.detuning
        self.ML_power = self.p.Delaystagescan.ML_power
        self.mode = self.p.Delaystagescan.mode
        self.average = int(self.p.Delaystagescan.average)
        self.x_values = self.get_scan_list(self.p.Delaystagescan.scan, 'V')
        self.init_volt = self.x_values[0]

    def program_pulser(self, sequence):
        pulse_sequence = sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_number(int(self.p.StateDetection.repititions))
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        counts = self.pulser.get_readout_counts()
        self.pulser.reset_readout_counts()
        return counts

    def finalize(self, cxn, context):
        self.pulser.frequency('369DP', self.init_cooling_freq)
        self.pulser.amplitude('DopplerCoolingSP', self.init_cooling_power)
        self.pulser.amplitude('ModeLockedSP', self.init_ML_power)
        self.keithley.gpib_write('Apply CH2,' + str(self.init_volt) + 'V')


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = Delaystagescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
