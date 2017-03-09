'''
### BEGIN NODE INFO
[info]
name = DAC AD660 Server
version = 1.0
description =
instancename = DAC AD660 Server
[startup]
cmdline = %PYTHON% %FILE%
timeout = 20
[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
'''

from labrad.server import LabradServer, setting, Signal, inlineCallbacks
from api import api
from config.dac_ad660_config import hardwareConfiguration as hc

SERVERNAME = 'DAC AD660 Server'
SIGNALID = 270837


class Voltage(object):
    def __init__(self, channel, analog_voltage=None, digital_voltage=None):
        self.channel = channel
        self.digital_voltage = digital_voltage
        self.analog_voltage = analog_voltage

    def program(self, set_num):
        '''
        Compute the hex code to program this voltage
        '''
        self.set_num = set_num
        if self.analog_voltage is not None:
            (vMin, vMax) = self.channel.allowedVoltageRange
            if self.analog_voltage < vMin:
                self.analog_voltage = vMin
            if self.analog_voltage > vMax:
                self.analog_voltage = vMax
            self.digital_voltage = self.channel.computeDigitalVoltage(self.analog_voltage)
        self.hex_rep = self.__getHexRep()

    def __getHexRep(self):
        port = bin(self.channel.dacChannelNumber)[2:].zfill(5)
        if hc.pulseTriggered:
            setN = bin(self.set_num)[2:].zfill(10)
        else:
            setN = bin(1)[2:].zfill(10)
        voltage = bin(self.digital_voltage)[2:].zfill(16)
        big = voltage + port + setN + '0'
        rep = chr(int(big[8:16], 2)) + chr(int(big[:8], 2)) + chr(int(big[24:32], 2)) + chr(int(big[16:24], 2))
        return rep


class Queue(object):
    def __init__(self):
        self.current_set = 1
        self.set_dict = {i: [] for i in range(1, hc.maxCache + 1)}

    def advance(self):
        self.current_set = (self.current_set % hc.maxCache) + 1

    def reset(self):
        self.current_set = 1

    def insert(self, v):
        ''' Always insert voltages to the current queue position, takes a voltage object '''
        v.program(self.current_set)
        self.set_dict[self.current_set].append(v)

    def get(self):
        v = self.set_dict[self.current_set].pop(0)
        return v

    def clear(self):
        self.current_set = 1
        self.set_dict = {i: [] for i in range(1, hc.maxCache + 1)}


class DACServer(LabradServer):
    """
    DAC Server
    Used for controlling DC trap electrodes
    """
    name = SERVERNAME
    onNewUpdate = Signal(SIGNALID, 'signal: ports updated', 's')
    queue = Queue()
    api = api()

    registry_path = ['', 'Servers', hc.EXPNAME + SERVERNAME]
    dac_dict = hc.elec_dict
    current_voltages = {}
    listeners = set()

    @inlineCallbacks
    def initServer(self):
        self.registry = self.client.registry
        self.initializeBoard()
        yield self.setCalibrations()

    def initializeBoard(self):
        connected = self.api.connectOKBoard()
        if not connected:
            raise Exception("FPGA Not Found")

    @inlineCallbacks
    def setCalibrations(self):
        ''' Go through the list of electrodes and try to detect calibrations '''
        yield self.registry.cd(self.registry_path + ['Calibrations'], True)
        subs, keys = yield self.registry.dir()
        for chan in self.dac_dict.values():
            c = []  # list of calibration coefficients in form [c0, c1, ..., cn]
            if str(chan.dacChannelNumber) in subs:
                yield self.registry.cd(self.registry_path + ['Calibrations',
                                                             str(chan.dacChannelNumber)])
                dirs, coeffs = yield self.registry.dir()
                for n in range(len(coeffs)):
                    e = yield self.registry.get('c'+str(n))
                    c.append(e)
                chan.calibration = c
            else:
                (vMin, vMax) = chan.boardVoltageRange
                prec = hc.PREC_BITS
                chan.calibration = [2**(prec - 1), float(2**(prec))/(vMax - vMin)]

    @setting(4, "Set Individual Digital Voltages", digital_voltages='*(si)')
    def setIndividualDigitalVoltages(self, c, digital_voltages):
        """
        Pass a list of tuples of the form:
        (portNum, newVolts)
        """
        for (port, dv) in digital_voltages:
            self.queue.insert(Voltage(self.dac_dict[port], digital_voltage=dv))
        yield self.writeToFPGA(c)

    @setting(5, "Set Individual Analog Voltages", analog_voltages='*(sv)')
    def setIndividualAnalogVoltages(self, c, analog_voltages):
        """
        Pass a list of tuples of the form:
        (portNum, newVolts)
        """
        for (port, av) in analog_voltages:
            self.queue.insert(Voltage(self.dac_dict[port], analog_voltage=av))
        yield self.writeToFPGA(c)

    def writeToFPGA(self, c):
        self.api.resetFIFODAC()
        for i in range(len(self.queue.set_dict[self.queue.current_set])):
            v = self.queue.get()
            self.api.setDACVoltage(v.hex_rep)
            if v.channel.name in hc.elec_dict.keys():
                self.current_voltages[v.channel.name] = v.analog_voltage
        if c is not None:
            self.notifyOtherListeners(c)

    @setting(9, "Get Analog Voltages", returns='*(sv)')
    def getCurrentVoltages(self, c):
        """
        Return the current voltage
        """
        return self.current_voltages.items()

    @setting(14, "Get DAC  Channel Name", port_number='i', returns='s')
    def getDACChannelName(self, c, port_number):
        '''
        Return the channel name for a given port port number.
        '''
        for key in self.dac_dict.keys():
            if self.dac_dict[key].dacChannelNumber == port_number:
                return key

    @setting(17, "get queue")
    def getQueue(self, c):
        return self.queue.current_set

    def initContext(self, c):
        self.listeners.add(c.ID)

    def expireContext(self, c):
        self.listeners.remove(c.ID)

    def notifyOtherListeners(self, context):
        notified = self.listeners.copy()
        try:
            notified.remove(context.ID)
        except:
            pass
        self.onNewUpdate('Channels updated', notified)

if __name__ == "__main__":
    from labrad import util
    util.runServer(DACServer())
