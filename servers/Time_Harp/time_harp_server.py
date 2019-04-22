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


if __name__ == "__main__":
    from labrad import util
    util.runServer(TimeHarpServer())
