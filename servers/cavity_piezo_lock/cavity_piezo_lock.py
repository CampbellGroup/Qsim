"""
### BEGIN NODE INFO
[info]
name = Cavity Piezo Lock
version = 1.0
description =
instancename = Cavity Piezo Lock

[startup]
cmdline = %PYTHON% %FILE%
timeout = 100

[shutdown]
message = 98765432
timeout = 100
### END

"""

import os
from labrad.server import LabradServer, setting
from labrad.units import WithUnit as U
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall

import socket
import numpy as np
import time


class cavity_piezo_lock(LabradServer):

    name = 'Cavity Piezo Lock'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Cavity Piezo Lock'
        self.chan = 1
        self.rate = 2
        self.start_time = time.time()
        self.sleep_time = 10
        self.voltage_history = []
        self.connect()
        self.lc = LoopingCall(self.loop)


    @inlineCallbacks
    def connect(self):
        '''
        Creates asynchronous connection
        '''
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync('10.97.112.4', name=self.name, password=self.password)
        self.wavemeter = self.cxn.multiplexerserver
        self.piezo = yield self.cxn.piezo_server
        self.piezo.select_device(0)
        self.set_point = yield self.wavemeter.get_frequency(1)
        self.lc.start(self.rate)

    @inlineCallbacks
    def loop(self):
        # piezo box set_voltage command returns voltage for some reason
        init_voltage = yield self.piezo.set_voltage(self.chan)
        init_voltage = U(float(init_voltage[1][-6:]), 'V')
        frequency_reading = yield self.wavemeter.get_frequency(1)
        delta = (self.set_point - frequency_reading)*1e6  # want the frequency in MHz for convenience

        if np.abs(delta) < 4.0:
            pass
        elif (delta < 0.0) and (np.abs(delta) < 15.0):
            delta_voltage = np.abs(delta)/10.0  # the cavity piezo is roughly 10 MHz/Volt
            set_voltage = init_voltage - U(delta_voltage, 'V')
            yield self.piezo.set_voltage(self.chan, set_voltage)
            self.voltage_history.append(set_voltage['V'])
            time.sleep(self.sleep_time)
        elif (delta > 0.0) and (np.abs(delta) < 15.0):
            delta_voltage = np.abs(delta)/10.0  # the cavity piezo is roughly 10 MHz/Volt
            set_voltage = init_voltage + U(delta_voltage, 'V')
            yield self.piezo.set_voltage(self.chan, set_voltage)
            self.voltage_history.append(set_voltage['V'])
            time.sleep(self.sleep_time)

    @setting(3014, 'get_voltage_history', returns='*v[]')
    def get_voltage_history(self, c):
        yield None
        returnValue(self.voltage_history)

    @setting(3015, 'set_sleep_time', sleep_time='i')
    def set_sleep_time(self, c, sleep_time):
        self.sleep_time = sleep_time

    @setting(3016, 'set_lock_frequency', lock_frequency='v')
    def set_lock_frequency(self, c, lock_frequency):
        self.set_point = lock_frequency

if __name__ == "__main__":
    from labrad import util
    util.runServer(cavity_piezo_lock())