from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time
import socket
import os
import labrad
import numpy as np


class lasermonitor(QsimExperiment):
    """
    Plots the change in a laser's frequency as a function of time relative
    to the initial laser frequency reading. Can be extended to any wavemeter that
    has a Labrad server
    """

    name = 'Laser Monitor'

    exp_parameters = []
    exp_parameters.append(('LaserMonitor', 'laser'))
    exp_parameters.append(('LaserMonitor', 'measure_time'))
    exp_parameters.append(('LaserMonitor', 'averaging_time'))

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.cxnwlm = labrad.connect('10.97.112.2', name=socket.gethostname() + " Laser Monitor", password=os.environ['LABRADPASSWORD'])
        self.cxn369 = labrad.connect('10.97.112.4', name=socket.gethostname() + " Laser Monitor", password=os.environ['LABRADPASSWORD'])
        self.wlm = self.cxnwlm.multiplexerserver
        self.wlm369 = self.cxn369.multiplexerserver
        self.chan_dict = {'369': 1, '760_1': 5, '935': 4, '399': 1, '760_2': 3, '822': 2, '976': 7}

    def run(self, cxn, context):

        '''
        Main loop
        '''

        self.inittime = time.time()
        if self.p.LaserMonitor.laser in ['369', '399']:
            self.initfreq = self.wlm369.get_frequency(1)
            print self.initfreq
        else:
            self.initfreq = self.wlm.get_frequency(self.chan_dict[str(self.p.LaserMonitor.laser)])
            print self.initfreq

        self.setup_datavault('Elapsed Time', 'Frequency Deviation')
        self.setup_grapher('Frequency Monitor')
        while (time.time() - self.inittime) <= self.p.LaserMonitor.measure_time['s']:
            should_stop = self.pause_or_stop()
            if should_stop:
                break

            freq_list = []
            init_averaging_time = time.time()
            # get the laser frequency from the correct wavemeter
            if self.p.LaserMonitor.laser in ['369', '399']:
                while (time.time() - init_averaging_time) < self.p.LaserMonitor.averaging_time['s']:
                    freq_list.append(self.wlm369.get_frequency(1))
            else:
                while (time.time() - init_averaging_time) < self.p.LaserMonitor.averaging_time['s']:
                    freq_list.append(self.wlm.get_frequency(self.chan_dict[str(self.p.LaserMonitor.laser)]))

            # find the average laser frequency over the measurement time
            freq = np.mean(freq_list)

            # try to add the data to datavault in MHz
            try:
                self.dv.add(time.time() - self.inittime, 1e6*(freq - self.initfreq))
            except:
                pass

            progress = float(time.time() - self.inittime)/self.p.LaserMonitor.measure_time['s']
            self.sc.script_set_progress(self.ident, progress)

    def finalize(self, cxn, context):
        self.cxnwlm.disconnect()
        self.cxn369.disconnect()



if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = lasermonitor(cxn=cxn)
    print exprt.name
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
