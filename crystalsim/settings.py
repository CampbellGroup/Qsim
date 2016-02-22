import numpy as np
class settings:
    rnot = 512e-6       
    V = 200
    m = 2.89e-25
    RF_freq = 40e6
    
    def print_settings(self):
        print 'Characteristic Distance(m): ', self.rnot
        print 'Voltage Amplitude (V): ', self.V
        print 'mass (kg): ', self.m
        print 'Frequency (Hz): ', self.RF_freq