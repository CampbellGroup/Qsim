"""
### BEGIN NODE INFO
[info]
name = windfreak
version = 1.0
description =
instancename = windfreak

[startup]
cmdline = %PYTHON% %FILE%
timeout = 5

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from labrad.types import Value
from labrad.devices import DeviceServer, DeviceWrapper
from labrad.server import setting
from twisted.internet.defer import inlineCallbacks, returnValue

TIMEOUT = Value(5.0, 's')

API = {
        # name              type    write      read
        'channel': (int, 'C{}\n', 'C?\n'),  # Select channel
        'frequency': (float, 'f{:.8f}\n', 'f?\n'),  # Frequency in MHz
        'power': (float, 'W{:.3f}\n', 'W?\n'),  # Power in dBm
        'calibrated': (bool, None, 'V\n'),
        'temp_comp_mode': (int, 'Z{}\n', 'Z?\n'),
        'vga_dac': (int, 'a{}\n', 'a?\n'),  # VGA DAC value [0, 45000]
        'phase_step': (float, '~{:.3f}\n', '~?\n'),  # Phase step in degrees
        'rf_enable': (bool, 'h{}\n', 'h?\n'),
        'pa_power_on': (bool, 'r{}\n', 'r?\n'),
        'pll_power_on': (bool, 'E{}\n', 'E?\n'),
        'model_type': (str, None, '+\n'),  # Model type
        'serial_number': (int, None, '-\n'),  # Serial number
        'fw_version': (str, None, 'v0\n'),  # Firmware version
        'hw_version': (str, None, 'v1\n'),  # Hardware version
        'sub_version': (str, None, 'v2\n'),  # Sub-version: "HD" or "HDPRO". Only Synth HD >= v2.
        'save': ((), 'e', None),  # Program all settings to EEPROM
        'reference_mode': (int, 'x{}\n', 'x?\n'),
        'trig_function': (int, 'w{}\n', 'w?\n'),
        'pll_lock': (bool, None, 'p\n'),
        'temperature': (float, None, 'z\n'),  # Temperature in Celsius
        'ref_frequency': (float, '*{:.8f}\n', '*?\n'),  # Reference frequency in MHz

        'sweep_freq_low': (float, 'l{:.8f}\n', 'l?\n'),  # Sweep lower frequency in MHz
        'sweep_freq_high': (float, 'u{:.8f}\n', 'u?\n'),  # Sweep upper frequency in MHz
        'sweep_freq_step': (float, 's{:.8f}\n', 's?\n'),  # Sweep frequency step in MHz
        'sweep_time_step': (float, 't{:.3f}\n', 't?\n'),  # Sweep time step in [4, 10000] ms
        'sweep_power_low': (float, '[{:.3f}\n', '[?\n'),  # Sweep lower power [-60, +20] dBm
        'sweep_power_high': (float, ']{:.3f}\n', ']?\n'),  # Sweep upper power [-60, +20] dBm
        'sweep_direction': (int, '^{}\n', '^?\n'),  # Sweep direction
        'sweep_diff_freq': (float, 'k{:.8f}\n', 'k?\n'),  # Sweep differential frequency in MHz
        'sweep_diff_meth': (int, 'n{}\n', 'n?\n'),  # Sweep differential method
        'sweep_type': (int, 'X{}\n', 'X?\n'),  # Sweep type {0: linear, 1: tabular}
        'sweep_single': (bool, 'g{}\n', 'g?\n'),
        'sweep_cont': (bool, 'c{}\n', 'c?\n'),

        'am_time_step': (int, 'F{}\n', 'F?\n'),  # Time step in microseconds
        'am_num_samples': (int, 'q{}\n', 'q?\n'),  # Number of samples in one burst
        'am_cont': (bool, 'A{}\n', 'A?\n'),  # Enable continuous AM modulation
        'am_lookup_table': ((int, float), '@{}a{:.3f}\n', '@{}a?\n'),  # Program row in lookup table in dBm

        'pulse_on_time': (int, 'P{}\n', 'P?\n'),  # Pulse on time in range [1, 10e6] us
        'pulse_off_time': (int, 'O{}\n', 'O?\n'),  # Pulse off time in range [2, 10e6] uS
        'pulse_num_rep': (int, 'R{}\n', 'R?\n'),  # Number of repetitions in range [1, 65500]
        'pulse_invert': (bool, ':{}\n', ':?\n'),  # Invert pulse polarity
        'pulse_single': ((), 'G\n', None),
        'pulse_cont': (bool, 'j{}\n', 'j?\n'),
        'dual_pulse_mod': (bool, 'D{}\n', 'D?\n'),

        'fm_frequency': (int, '<{}\n', '<?\n'),
        'fm_deviation': (int, '>{}\n', '>?\n'),
        'fm_num_samples': (int, ',{}\n', ',?\n'),
        'fm_mod_type': (int, ';{}\n', ';?\n'),
        'fm_cont': (bool, '/{}\n', '/?\n'),
    }

trigger_modes = (
    'disabled',
    'full frequency sweep',
    'single frequency step',
    'stop all',
    'rf enable',
    'remove interrupts',
    'reserved',
    'reserved',
    'am modulation',
    'fm modulation',
)

class windfreak_wrapper(DeviceWrapper):

    @inlineCallbacks
    def connect(self, server, port):
        """Connect to a Windfreak Device."""
        print('connecting to "%s" on port "%s"...' % (server.name, port),)
        self.server = server
        self.ctx = server.context()
        self.port = port
        p = self.packet()
        p.open(port)
        p.baudrate(38400)
        p.read()  # clear out the read buffer
        p.timeout(TIMEOUT)
        yield p.send()

    def packet(self):
        """Create a packet in our private context."""
        return self.server.packet(context=self.ctx)

    def shutdown(self):
        """Disconnect from the serial port when we shut down."""
        return self.packet().close().send()

    def read(self, attribute, *args):
        # get the command from the API
        dtype, _, request = API[attribute]
        dtype = dtype if isinstance(dtype, tuple) else (dtype,)
        # cast any bools as ints
        args = ((int(ar) if dt is bool else dt(ar)) for dt, ar in zip(dtype, args))
        # format the string to send, and query the device
        ret = yield self._query(request.format(*args))
        # check that the returned data makes sense
        dtype = dtype[-1]
        if dtype is bool:
            ret = int(ret)
            if ret not in (0, 1):
                raise ValueError('Invalid return value \'{}\' for type bool.'.format(ret))
        returnValue(dtype(ret))

    def write(self, attribute, *args):
        dtype, request, _ = API[attribute]
        dtype = dtype if isinstance(dtype, tuple) else (dtype,)
        if len(args) != len(dtype):
            raise ValueError('Number of arguments and data-types are not equal.')
        # cast any bools as ints
        args = ((int(ar) if dt is bool else dt(ar)) for dt, ar in zip(dtype, args))
        self._write(request.format(*args))

    @inlineCallbacks
    def _write(self, code):
        """Write a data value. """
        yield self.packet().write(code).send()

    @inlineCallbacks
    def _read(self):
        p = self.packet()
        p.read_line()
        ans = yield p.send()
        returnValue(ans.read_line())

    @inlineCallbacks
    def _query(self, code):
        """Write, then read. """
        p = self.packet()
        p.write_line(code)
        # p.read_line()
        ans = yield p.send()
        returnValue(ans.read_line())


class Windfreak_Server(DeviceServer):
    name = 'windfreak'
    deviceName = 'windfreak'
    deviceWrapper = windfreak_wrapper

    @inlineCallbacks
    def initServer(self):
        self.current_state = {}
        self.frequency = [0., 0.]
        self.power = [0., 0.]
        self.channel = 0
        self.onoff = [0, 0]
        self.phase = [0., 0.]
        print('loading config info...',)
        self.reg = self.client.registry()
        yield self.loadConfigInfo()
        yield DeviceServer.initServer(self)

        # self.set_reference_mode('internal 27mhz')
        # self.set_enable(0, True)
        # self.set_enable(0, False)
        # self.set_enable(1, True)
        # self.set_enable(1, False)

    @inlineCallbacks
    def loadConfigInfo(self):
        """Load configuration information from the registry."""
        reg = self.reg
        yield reg.cd(['', 'Servers', 'windfreak', 'Links'], True)
        dirs, keys = yield reg.dir()
        #print(dirs, keys)
        p = reg.packet()
        for k in keys:
            p.get(k, key=k)
            #print(p.get(k, key=k))
        ans = yield p.send()
        self.serialLinks = dict((k, ans[k]) for k in keys)
        # Get output state and last value of current set
        yield reg.cd(['', 'Servers', 'windfreak', 'parameters'], True)
        dirs, keys = yield reg.dir()
        p = reg.packet()
        for k in keys:
            p.get(k, key=k)
        ans = yield p.send()
        self.params = dict((k, ans[k]) for k in keys)
        for key in self.params:
            self.current_state[key] = list(self.params[key])

    @inlineCallbacks
    def findDevices(self):
        """Find available devices from list stored in the registry."""
        devs = []
        for name, (serServer, port) in self.serialLinks.items():
            if serServer not in self.client.servers:
                continue
            server = self.client[serServer]
            ports = yield server.list_serial_ports()
            print(ports)
            if port not in ports:
                continue
            devName = '%s - %s' % (serServer, port)
            devs += [(devName, (server, port))]
        returnValue(devs)

    @setting(11, prop='s', chan='i', returns='?')
    def get_property(self, c, prop, chan=None):
        dev = self.selectDevice(c)
        if chan is not None:
            yield self.set_channel(c, chan)
        message = yield dev.read(prop)
        try:
            returnValue(message)
        except Exception:
            returnValue("Something went wrong, cannot get {}".format(prop))

    @setting(12, prop='s', val='?', chan='i')
    def set_property(self, c, prop, val, chan=None):
        dev = self.selectDevice(c)
        if chan is not None:
            yield self.set_channel(c, chan)
        yield dev.write(prop, val)

    @setting(13, returns='s')
    def get_channel(self, c):
        returnValue(self.get_property(c, 'channel'))

    @setting(14, channel='i')
    def set_channel(self, c, channel):
        if channel > 1 or channel < 0:
            returnValue('Channel number needs to be 0 or 1')
        else:
            self.channel = channel
            yield self.set_property(c, 'channel', channel)

    @setting(15, channel='i', returns='v')
    def get_freq(self, c, channel):
        returnValue(self.get_property(c, 'frequency', chan=channel))

    @setting(16, channel='i', freq='v')
    def set_freq(self, c, channel, freq):
        if freq < 53.0 or freq > 13999.999999:
            returnValue('Frequency must be between 53.0 and 13999.999999MHz.')
        else:
            self.frequency[channel] = freq
            yield self.set_property(c, 'frequency', freq, chan=channel)

    @setting(17, channel='i', returns='v')
    def get_phase(self, c, channel):
        returnValue(self.get_property(c, 'phase_step', chan=channel))

    @setting(18, channel='i', phase='v')
    def set_phase(self, c, channel, phase):
        if phase < 0. or phase > 360:
            returnValue('Phase must be between 0 and 360 degrees')
        else:
            self.phase[channel] = phase
            yield self.set_property(c, 'phase_step', phase, chan=channel)

    @setting(19, channel='i', returns='v')
    def get_power(self, c, channel):
        returnValue(self.get_property(c, 'power', chan=channel))

    @setting(20, channel='i', p='v')
    def set_power(self, c, channel, p):
        if p < -60.0 or p > 20.:
            returnValue('Power must be between -60.0 and 20dBm.')
        else:
            self.power[channel] = p
            yield self.set_property(c, 'power', p, chan=channel)

    @setting(21, channel='i', returns='b')
    def get_rf_enable(self, c, channel):
        returnValue(self.get_property(c, 'rf_enable', chan=channel))

    @setting(22, channel='i', val='b')
    def set_rf_enable(self, c, channel, val):
        self.onoff[channel] = (1 if val else 0)
        yield self.set_property(c, 'rf_enable', val, chan=channel)

    @setting(23, channel='i', returns='b')
    def get_pa_enable(self, c, channel):
        returnValue(self.get_property(c, 'pa_power_on', chan=channel))

    @setting(24, channel='i', val='b')
    def set_pa_enable(self, c, channel, val):
        self.onoff[channel] = (1 if val else 0)
        yield self.set_property(c, 'pa_power_on', val, chan=channel)

    @setting(25, channel='i', returns='b')
    def get_pll_enable(self, c, channel):
        returnValue(self.get_property(c, 'pll_power_on', chan=channel))

    @setting(26, channel='i', val='b')
    def set_pll_enable(self, c, channel, val):
        self.onoff[channel] = (1 if val else 0)
        yield self.set_property(c, 'pll_power_on', val, chan=channel)

    @setting(27, channel='i', returns='b')
    def get_enable(self, c, channel):
        returnValue(self.get_rf_enable(c, channel) and self.get_pa_enable(c, channel) and self.get_pll_enable(c, channel))

    @setting(28, channel='i', val='b')
    def set_enable(self, c, channel, val):
        yield self.set_rf_enable(c, channel, val)
        yield self.set_pa_enable(c, channel, val)
        yield self.set_pll_enable(c, channel, val)

    @setting(29, returns='s')
    def get_reference_mode(self, c):
        returnValue(self.get_property(c, 'reference_mode'))

    @setting(30, mode='s')
    def set_reference_mode(self, c, mode):
        if mode not in ('external', 'internal 27mhz', 'internal 10mhz'):
            raise ValueError('Expected str in set ("external", "internal 27mhz", "internal 10mhz")')
        yield self.set_property(c, 'reference_mode', ('external', 'internal 27mhz', 'internal 10mhz').index(mode))

    @setting(31, returns='s')
    def get_trigger_mode(self, c):
        returnValue(trigger_modes[self.get_property(c, 'trig_function')])

    @setting(32, mode='s')
    def set_trigger_mode(self, c, mode):
        if mode not in trigger_modes:
            raise ValueError('Expected str in set {}.'.format(trigger_modes))
        yield self.set_property(c, 'trig_function', trigger_modes.index(mode))

    @setting(33, returns='v')
    def get_temperature(self, c):
        returnValue(self.get_property(c, 'temperature'))

    @setting(34, returns='v')
    def get_reference_frequency(self, c):
        returnValue(self.get_property(c, 'ref_frequency'))

    @setting(35, freq='v')
    def set_reference_frequency(self, c, freq):
        if freq < 10.0 or freq > 100.0:
            returnValue("reference frequency must be between 10 and 100 MHz")
        yield self.set_property(c, 'ref_frequency', freq)

    # TODO: temp compensation modes

    # TODO: vga dac stuff

    # TODO: Sweep and modulation




__server__ = Windfreak_Server()

if __name__ == "__main__":
    from labrad import util

    util.runServer(__server__)
