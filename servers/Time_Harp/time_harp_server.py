"""
### BEGIN NODE INFO
[info]
name = Time Harp Server
version = 1.0
description =
instancename = Time Harp Server

[startup]
cmdline = %PYTHON% %FILE%self.wmdll.SetPIDCourseNum
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer, setting
from twisted.internet.defer import returnValue
import ctypes


class TimeHarpServer(LabradServer):
    """
    Time harp fast time tagging server.
    """

    name = 'TimeHarpServer'

    def initServer(self):
        # load timeharp dll file
        dll_path = 'C:\Windows\System32\TH260Lib.DLL'
        self.device_index = ctypes.c_int(0)
        self.thdll = ctypes.windll.LoadLibrary(dll_path)

    @setting(1, "get_errors")
    def get_errors(self, c):
        func = self.thdll.TH260_GetErrorString
        func.restype = ctypes.c_int
        errstring = ctypes.create_string_buffer(40)
        errcode = ctypes.c_int()
        yield func(errstring, errcode)
        returnValue((errstring.value, errcode.value))

    @setting(2, "get_version")
    def get_version(self, c):
        func = self.thdll.TH260_GetLibraryVersion
        func.restype = ctypes.c_int
        vers_string = ctypes.create_string_buffer(8)
        yield func(vers_string)
        returnValue(vers_string.value)

    @setting(3, "open_device")
    def open_device(self, c):
        func = self.thdll.TH260_OpenDevice
        func.restype = ctypes.c_int
        serial = ctypes.create_string_buffer(8)
        output = yield func(self.device_index, serial)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(4, "close_device")
    def close_device(self, c):
        func = self.thdll.TH260_CloseDevice
        func.restype = ctypes.c_int
        output = yield func(self.device_index)
        if output.value == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(5, "initialize", mode='w')
    def initialize(self, c, mode):
        """ initialize device with specified mode: 0 = histogramming mode, 2 = T2 mode, 3 = T3 mode """
        if mode in [0, 2, 3]:
            mode = ctypes.c_int(mode)
            func = self.thdll.TH260_Initialize
            func.restype = ctypes.c_int
            output = func(self.device_index, mode)
            if output.value == 0:
                returnValue('Success!')
            else:
                returnValue('Failure')

    @setting(6, "get_hardware_info")
    def get_hardware_info(self, c):
        """ get hardware info. returns model, part number, version"""
        func = self.thdll.TH260_GetHardwareInfo
        func.restype = ctypes.c_int
        model = ctypes.create_string_buffer(16)
        partno = ctypes.create_string_buffer(8)
        version = ctypes.create_string_buffer(16)
        output = yield func(self.device_index, model, partno, version)
        if output.value == 0:
            returnValue((model.value, partno.value, version.value))
        else:
            returnValue('Failure')

    @setting(7, "get_serial_number")
    def get_serial_number(self, c):
        func = self.thdll.TH260_GetSerialNumber
        func.restype = ctypes.c_int
        serial = ctypes.create_string_buffer(8)
        output = yield func(self.device_index, serial)
        if output.value == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(8, "get_features")
    def get_features(self, c):
        func = self.thdll.TH260_GetFeatures
        func.restype = ctypes.c_int
        flags = ctypes.c_int()
        output = yield func(self.device_index, flags)
        if output.value == 0:
            returnValue(flags.value)
        else:
            returnValue('Failure')

    @setting(9, "get_base_resolution")
    def get_base_resolution(self, c):
        "returns the base resolution in ps and the maximally allowed binning steps"
        func = self.thdll.TH260_GetBaseResolution
        func.restype = ctypes.c_int
        resolution = ctypes.c_double()
        bin_steps = ctypes.c_int()
        output = yield func(self.device_index, resolution, bin_steps)
        if output.value == 0:
            returnValue((resolution.value, bin_steps.value))
        else:
            returnValue('Failure')

    @setting(10, "get_num_channels")
    def get_num_channels(self, c):
        "returns the number of installed input channels"
        func = self.thdll.TH260_GetNumOfInputChannels
        func.restype = ctypes.c_int
        n_channels = ctypes.c_int()
        output = yield func(self.device_index, n_channels)
        if output.value == 0:
            returnValue(n_channels.value)
        else:
            returnValue('Failure')

    @setting(11, "set_timing_mode", mode='w')
    def set_timing_mode(self, c, mode):
        "changes timing mode from: 0 = Hires (25ps) to 1 = Lowres (2.5ns)"
        func = self.thdll.TH260_SetTimingMode
        func.restype = ctypes.c_int
        mode = ctypes.c_int(mode)
        output = yield func(self.device_index, mode)
        if output.value == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')


if __name__ == "__main__":
    from labrad import util
    util.runServer(TimeHarpServer())
