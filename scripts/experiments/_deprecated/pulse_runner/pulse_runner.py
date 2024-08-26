
import labrad
from Qsim.scripts.experiments.qsim_pulse_experiment import QsimPulseExperiment
from Qsim.scripts.pulse_sequences.bright_state_preperation import bright_state_preperation as sequence

class test_exp(QsimPulseExperiment):


    name = 'Test Pulse Experiment'

    exp_parameters = []
    exp_parameters.extend(sequence.all_required_parameters())

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = test_exp(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)