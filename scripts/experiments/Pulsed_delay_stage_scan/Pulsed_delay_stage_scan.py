import labrad
import numpy as np
from Qsim.scripts.pulse_sequences.ML_interrogation_point import ML_interrogation_point as ml_interrogation_point
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time
from labrad.units import WithUnit as U


class Pulsed_delay_stage_scan(QsimExperiment):

    name = 'Pulsed Delay Stage Scan'

    exp_parameters = []
    exp_parameters.append(('Delaystagescan', 'scan'))
    exp_parameters.append(('Delaystagescan', 'average'))
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('DopplerCooling', 'cooling_power'))
    exp_parameters.append(('DopplerCooling', 'repump_power'))
    exp_parameters.append(('Delaystagescan', 'ML_power'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('MLStateDetection', 'repititions'))
    exp_parameters.append(('MLStateDetection', 'points_per_histogram'))
    exp_parameters.append(('MLStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('bf_fluorescence', 'crop_start_time'))
    exp_parameters.append(('bf_fluorescence', 'crop_stop_time'))
    exp_parameters.append(('Delaystagescan', 'state_prep'))
    exp_parameters.extend(ml_interrogation_point.all_required_parameters())

    def initialize(self, cxn, context, ident):

        self.ident = ident

        self.chan = 2
        self.keithley = self.cxn.keithley_2230g_server
        self.keithley.select_device(0)

        #self.piezo_server = self.cxn.piezo_server

#        self.init_ML_power = self.pulser.amplitude('ModeLockedSP')
        self.init_cooling_freq = self.pulser.frequency('369DP')
        self.init_cooling_power = self.pulser.amplitude('369DP')

    def run(self, cxn, context):
        '''
        Main loop
        '''
        self.set_scannable_parameters()
        self.keithley.gpib_write('Apply CH2,' + str(self.init_volt) + 'V')
        self.keithley.output(self.chan, True)
        #self.piezo_server.set_voltage(self.chan, U(self.init_volt, 'V'))
        self.path = self.setup_datavault('Volts', 'counts')
        self.setup_grapher('Ramsey Delay Stage Piezo Scan')

        try:
            MLfreq = cxn.bristol_521.get_wavelength()
            self.dv.add_parameter('Bristol Reading', MLfreq)
        except:
            pass

        for i, volt in enumerate(self.x_values):
            should_break = self.update_progress(i/float(len(self.x_values)))
            if should_break:
                break
            # we write direct GPIB for speed
            self.keithley.gpib_write('APPLy CH2,' + str(volt) + 'V')
            # self.piezo_server.set_voltage(self.chan, U(volt, 'V'))
            time.sleep(0.1)
            # once delay stage is set, program sequence to interrogate and get counts
            self.program_pulser(ml_interrogation_point)
            counts = self.run_ML_sequence()
            self.dv.add(volt, float(counts)/self.p.MLStateDetection.repititions)

    def set_scannable_parameters(self):
        '''
        gets parameters, called in run so scan works
        '''

        self.cooling_power = self.p.DopplerCooling.cooling_power
        self.cooling_center = self.p.Transitions.main_cooling_369/2. + U(200.0, 'MHz')
        self.detuning = self.p.DopplerCooling.detuning
        self.ML_power = self.p.Delaystagescan.ML_power
        self.mode = self.p.Delaystagescan.mode
        self.average = int(self.p.Delaystagescan.average)
        self.x_values = self.get_scan_list(self.p.Delaystagescan.scan, 'V')
        self.init_volt = self.x_values[0]

    def run_ML_sequence(self, max_runs=1000, num=1):
        reps = self.p.MLStateDetection.repititions

        self.timeharp.start_measure(60000)
        self.pulser.start_number(int(reps))
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        self.pulser.reset_readout_counts()
        time.sleep(0.1)
        self.timeharp.stop_measure()
        data = self.timeharp.read_fifo(131072)
        stamps = data[0]
        data_length = data[1]
        stamps = stamps[0:data_length]
        timetags = self.convert_timetags(stamps)

        while data_length > 0:
            data = self.timeharp.read_fifo(131072)
            stamps = data[0]
            data_length = data[1]
            stamps = stamps[0:data_length]
            timetags += self.convert_timetags(stamps)

        low = self.p.bf_fluorescence.crop_start_time['ns']
        high = self.p.bf_fluorescence.crop_stop_time['ns']
        cropped_timetags = sum([low <= item <= high for item in timetags])
        return cropped_timetags

    def finalize(self, cxn, context):
        self.keithley.gpib_write('Apply CH2,' + str(self.init_volt) + 'V')
        #self.piezo_server.set_voltage(self.chan, U(self.init_volt, 'V'))

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = Pulsed_delay_stage_scan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
