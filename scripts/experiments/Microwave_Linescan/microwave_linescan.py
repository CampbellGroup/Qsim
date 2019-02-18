import labrad
from Qsim.scripts.pulse_sequences.microwave_point import microwave_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U


class MicrowaveLineScan(QsimExperiment):
    """
    Scan 12.6 GHz microwave source over the qubit transition
    """

    name = 'Microwave Line Scan'

    exp_parameters = []
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))

    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.append(('StateDetection', 'state_readout_threshold'))
    exp_parameters.append(('MicrowaveLinescan', 'scan'))

    exp_parameters.append(('StateDetection', 'points_per_histogram'))

    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.append(('Pi_times', 'qubit_plus'))
    exp_parameters.append(('Pi_times', 'qubit_minus'))
    
    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.remove(('MicrowaveInterogation', 'detuning')) 
    exp_parameters.remove(('MicrowaveInterogation', 'duration'))

    
    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('frequency', 'probability')  # gives the x and y names to Data Vault
        qubit = self.p.Line_Selection.qubit
        self.setup_grapher('Microwave Linescan ' + qubit)
        self.detunings = self.get_scan_list(self.p.MicrowaveLinescan.scan, 'kHz')

        if qubit == 'qubit_0':
            center = self.p.Transitions.qubit_0
            pi_time = self.p.Pi_times.qubit_0

        elif qubit == 'qubit_plus':
            center = self.p.Transitions.qubit_plus
            pi_time = self.p.Pi_times.qubit_plus

        elif qubit == 'qubit_minus':
            center = self.p.Transitions.qubit_minus
            pi_time = self.p.Pi_times.qubit_minus

        self.p['MicrowaveInterogation.duration'] = pi_time
        
        for i, detuning in enumerate(self.detunings):
            should_break = self.update_progress(i/float(len(self.detunings)))
            if should_break:
                break
            self.p['MicrowaveInterogation.detuning'] = U(detuning, 'kHz')
            self.program_pulser(sequence)
            counts = self.run_sequence()
            if i % self.p.StateDetection.points_per_histogram == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist)
            pop = self.get_pop(counts)
            
            self.dv.add(detuning + center['kHz'], pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveLineScan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
