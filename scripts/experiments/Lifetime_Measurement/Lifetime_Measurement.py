import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time
import numpy as np

#__scriptscanner_name_ = 'Lifetime_Measurement'

class Lifetime_Measurement(QsimExperiment):

    name = 'Lifetime Measurement'

    exp_parameters = []
    exp_parameters.append(('Loading', 'ion_threshold'))

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.pmt = self.cxn.normalpmtflow
        self.pulser = self.cxn.pulser
        self.path = '/home/qsimexpcontrol/LabRAD/data/Lifetime_Measurements.dir/'

    def run(self, cxn, context):

        '''
        Main loop of experiment. This is simply intended to be run once the ion is loaded, and then as long as the integrated flouresence is higher than the loading threshold, it will continue. 
        '''

        if self.pmt.get_next_counts('ON', 10, True) > self.p.Loading.ion_threshold:
            counts = self.pmt.get_next_counts('ON', 10, True)
            start = time.time()
            while counts > self.p.Loading.ion_threshold:
                counts = self.pmt.get_next_counts('ON', 10, True)
            end = time.time()

        lifetime = str((end - start)/60.0) #lifetime in minutes
        with open(self.path + 'lifetimes.txt', 'a') as file:
            file.write(lifetime + ',')

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = Lifetime_Measurement(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
