import labrad
from Qsim.abstractdevices.script_scanner.scan_methods import experiment
import time

class arduino_test(experiment):
    
    name = 'test experiment'
    
    required_parameters =[]#('light show', 'speed')] 
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = "test script")
        self.dv = cxn.data_vault
        self.ad = cxn.arduinottl
        
        self.speed = 1 #self.parameters.light_show.speed
#        self.order = self.parameters.light_show.orderQsi
#        self.onlights = self.parameters.light_show.on_lights
        
    def run(self, cxn, context):
        print self.speed
        self.ad.ttl_output(2, True)
        time.sleep(self.speed)
        self.ad.ttl_output(3, True)
        time.sleep(self.speed)
        self.ad.ttl_output(4, True)
        time.sleep(self.speed)
        self.ad.ttl_output(2, False)
        self.ad.ttl_output(3, False)
        self.ad.ttl_output(4, False)
        
    def finalize(self, cxn, context):
        self.cxn.disconnect()
        
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = arduino_test(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)