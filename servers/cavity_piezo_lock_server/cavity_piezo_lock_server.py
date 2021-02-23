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


class cavity_piezo_lock_server(LabradServer):

    name = 'Cavity Piezo Lock Server'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Cavity Piezo Lock Server'
        self.chan = 1
        self.rate = 1
        self.start_time = time.time()
        self.sleep_time = 0.01
        self.max_voltage = U(50.0, 'V')
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
        self.sleep_time = 2.0
        self.piezo.select_device(0)
        self.set_point = yield self.wavemeter.get_frequency(1)
        self.lc.start(self.rate)
        self.init_time = time.time()

    @inlineCallbacks
    def loop(self):
        # piezo box set_voltage command returns voltage for some reason
        init_voltage = yield self.piezo.get_voltage(self.chan)
        init_voltage = U(float(init_voltage), 'V')
        frequency_reading = yield self.wavemeter.get_frequency(1)
        delta = (frequency_reading - self.set_point)*1e6  # want the frequency in MHz for convenience

        if time.time() < self.init_time + 2.0:
            print self.set_point

        if np.abs(delta) < 2.0:
            # dont do anything if within a certain range
            pass

        elif (delta < 0.0) and (np.abs(delta) < 40.0):
            delta_voltage = 0.01
            set_voltage = init_voltage - U(delta_voltage, 'V')
            if set_voltage <= self.max_voltage:
                yield self.piezo.set_voltage(self.chan, set_voltage)
                self.voltage_history.append([time.time() - self.init_time, set_voltage['V']])
            elif set_voltage > self.max_voltage:
                print 'Maximum voltage exceeded'
            time.sleep(self.sleep_time)

        elif (delta > 0.0) and (np.abs(delta) < 40.0):
            delta_voltage = 0.01
            set_voltage = init_voltage + U(delta_voltage, 'V')
            if set_voltage <= self.max_voltage:
                yield self.piezo.set_voltage(self.chan, set_voltage)
                self.voltage_history.append([time.time() - self.init_time, set_voltage['V']])
            elif set_voltage > self.max_voltage:
                print 'Maximum voltage exceeded'
            time.sleep(self.sleep_time)

        elif delta > 40.0:
            self.lc.stop()
            print('Laser is outside programmed bandwidth of lock, killing loop.')

    @setting(3014, 'get_voltage_history', returns='*2v[]')
    def get_voltage_history(self, c):
        """
        Returns a list of times and voltages for backing out the history of voltage changes
        """
        yield None
        returnValue(self.voltage_history)

    @setting(3015, 'set_sleep_time', sleep_time='i')
    def set_sleep_time(self, c, sleep_time):
        self.sleep_time = sleep_time

    @setting(3016, 'set_lock_frequency', lock_frequency='v')
    def set_lock_frequency(self, c, lock_frequency):
        self.set_point = lock_frequency

    @setting(3017, 'stop_lock_loop')
    def stop_lock_loop(self, c):
        self.lc.stop()


if __name__ == "__main__":
    from labrad import util
    util.runServer(cavity_piezo_lock_server())