import labrad
import numpy as np
from Qsim.scripts.pulse_sequences.bright_state_preperation import bright_state_preperation as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment


class BrightStateDetection(QsimExperiment):
    """
    Doppler cool ion the readout bright fidelity
    """

    name = 'Bright State Detection'

    exp_parameters = []
    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pmt = self.cxn.normalpmtflow
        self.init_mode = self.pmt.getcurrentmode()
        self.pmt.set_mode('Normal')
        self.pulser = self.cxn.pulser
        self.dv.cd(['','Bright_State_Detection'], True)

    def run(self, cxn, context):

        self.program_pulser()

    def program_pulser(self):

        pulse_sequence = sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_number(int(self.p.StateDetection.repititions))
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        counts = self.pulser.get_readout_counts()
        self.pulser.reset_readout_counts()
        dataset = self.dv.new('bright_state_detection', [('run', 'arb u')], [('Counts', 'Counts', 'num')])
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter])
        data = np.column_stack((np.arange(self.p.StateDetection.repititions),counts))
        self.dv.add(data)
        self.dv.add_parameter('isHistogram', True)


    def finalize(self, cxn, context):
        self.pmt.set_mode(self.init_mode)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = BrightStateDetection(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
