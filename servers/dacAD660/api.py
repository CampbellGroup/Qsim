import ok.ok as ok
from config.dac_ad660_config import HardwareConfiguration

error_codes = {
    0: "ok_NoError",
    -1: "ok_Failed",
    -2: "ok_Timeout",
    -3: "ok_DoneNotHigh",
    -4: "ok_TransferError",
    -5: "ok_CommunicationError",
    -6: "ok_InvalidBitstream",
    -7: "ok_FileError",
    -8: "ok_DeviceNotOpen",
    -9: "ok_InvalidEndpoint",
    -10: "ok_InvalidBlockSize",
    -11: "ok_I2CRestrictedAddress",
    -12: "ok_I2CBitError",
    -13: "ok_I2CNack",
    -14: "ok_I2CUnknownStatus",
    -15: "ok_UnsupportedFeature",
    -16: "ok_FIFOUnderflow",
    -17: "ok_FIFOOverflow",
    -18: "ok_DataAlignmentError"
}


class API:
    """class containing all commands for interfacing with the fpga"""

    def __init__(self):
        self.xem = None
        self.okDeviceID = HardwareConfiguration.okDeviceID
        self.okDeviceFile = HardwareConfiguration.okDeviceFile

    def check_connection(self):
        if self.xem is None:
            raise Exception("FPGA not connected")

    def connect_ok_board(self) -> bool:
        fp = ok.FrontPanel()
        module_count = fp.GetDeviceCount()
        print("Found {} opalKelly modules".format(module_count))
        for i in range(module_count):
            serial = fp.GetDeviceListSerial(i)
            tmp = ok.FrontPanel()
            tmp.OpenBySerial(serial)
            iden = tmp.GetDeviceID()
            if iden == self.okDeviceID:
                self.xem = tmp
                print('Connected to {}'.format(iden))
                self.program_ok_board()
                return True
        return False

    def program_ok_board(self) -> None:
        prog = self.xem.ConfigureFPGA(self.okDeviceFile)
        if prog != 0:
            raise Exception("Not able to program FPGA. error code: {} {}".format(prog, error_codes[prog]))
        pll = ok.PLL22150()
        self.xem.GetEepromPLL22150Configuration(pll)
        pll.SetDiv1(pll.DivSrc_VCO, 4)
        self.xem.SetPLL22150Configuration(pll)

    def program_board(self, sequence: bytearray) -> None:
        sequence_data = self.pad_to_16(sequence)
        self.xem.WriteToBlockPipeIn(0x80, 16, sequence_data)

    def reset_fifo_dac(self) -> None:
        self.xem.ActivateTriggerIn(0x40, 8)

    def set_dac_voltage(self, volstr: bytearray) -> None:
        volstr_padded = self.pad_to_16(volstr)
        # print("volstr_padded:", volstr_padded.hex(sep=":"))
        self.xem.WriteToBlockPipeIn(0x82, 16, volstr_padded)

    def pad_to_16(self, data: bytearray) -> bytearray:
        """
        Padding function to make the data a multiple of 16 bytes
        """
        size_needed = (16 - len(data) % 16) % 16
        zero_padding = bytearray(size_needed)
        return data + zero_padding
