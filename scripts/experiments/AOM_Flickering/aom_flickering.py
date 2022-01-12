import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time


class aom_flickering(QsimExperiment):
    """
    Literally just toggle an AOM on and off forever.
    You can choose which AOM to toggle, and how long to toggle it.
    """

    name = 'AOM Flickering'

    exp_parameters = [('AOMFlickering', 'flicker_time'),
                      ('AOMFlickering', 'duty_cycle'),
                      ('AOMFlickering', 'aom_selection')]

    def initialize(self, cxn, context, identity):
        self.ident = identity
        self.reg = cxn.registry
        self.reg.cd(['', 'settings'])

    def run(self, cxn, context):
        on_time = self.p.AOMFlickering.flicker_time * self.p.AOMFlickering.duty_cycle
        off_time = self.p.AOMFlickering.flicker_time - on_time
        while True:
            self.pulser.output(self.p.AOMFlickering.aom_selection, True, context=self.context)
            time.sleep(on_time['s'])
            should_break = self.update_progress(0.5)
            if should_break:
                return should_break
            self.pulser.output(self.p.AOMFlickering.aom_selection, False, context=self.context)
            time.sleep(off_time['s'])

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = aom_flickering(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
