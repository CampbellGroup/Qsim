"""
### BEGIN NODE INFO
[info]
name = AWG Windows Server
version = 1.3
description =


[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

import socket
from labrad.server import LabradServer
from labrad.server import setting

from labrad.types import Value
from labrad.server import setting
from twisted.internet.defer import inlineCallbacks, returnValue


def args_to_csv_strings(arguments):
    """Takes a list of arguments and converts them to strings so that they can be sent as a command to the AWG Windows server.

    Args:
        arguments (list): list of non-string arguments

    Returns:
        string: arguments converted to a string with formatting for the AWG Windows server.
    """
    argument_string = ""
    for arg in arguments:
        argument_string += str(arg) + ","
    argument_string = argument_string.replace(" ", "")
    return argument_string[:-1]


class AWG_Windows_Server(LabradServer):
    """
    Connect to Windows computer on the AWG.
    """

    name = "AWG Windows Server"

    def initServer(self):
        self.name = "AWG Windows Server"
        self.socket_timeout = 20  # seconds
        self.connect_to_AWG()

    def connect_to_AWG(self):
        """ """
        HOST = "10.97.112.113"
        PORT = 4001
        self.WaveForm_folder_path = "C:/Users/tek_local_admin/Documents/WaveForm/"  # location of waveform txt files on AWG computer

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((HOST, PORT))
        self.server.settimeout(self.socket_timeout)

    @inlineCallbacks
    def send_command(self, command, receive=False):
        """Sends string commands to the AWG windows server.

        Args:
            command (string): must follow same syntax as the AWG instrument.
            receive (bool, optional): Receive and print data from AWG windows server if True. Defaults to False.
        """
        yield self.server.sendall(
            command.encode("utf-8")
        )  # send command with utf-8 string encoding
        if receive:  # print received data if True
            yield self.server.recv(1024)

    @setting(3334, "send command", command="s", receive="b")
    def send_command_raw(self, c, command, receive=False):
        """Sends string commands to the AWG windows server.

        Args:
            command (string): must follow same syntax as the AWG instrument.
            receive (bool, optional): Receive and print data from AWG windows server if True. Defaults to False.
        """
        self.server.sendall(
            command.encode("utf-8")
        )  # send command with utf-8 string encoding
        if receive:  # print received data if True
            data = self.server.recv(1024)
            print(data)

    @setting(
        2,
        "make multitone text",
        frequency_spacings="*?",
        frequency_offset="v",
        sample_rate="v",
        file_name="s",
    )
    def make_multitone_text(self, c, frequency_spacings, frequency_offset, sample_rate, file_name):
        """Sends a string command to the AWG Windows server that calls a function to write and save the
        desired multitone waveform as a text file.

        Args:
            frequency_spacings (list): list of frequencies (Hz) to include in the multitone signal
            frequency_offset (float): a single frequency to add to each frequency in 'frequency_spacings'
            sample_rate (float): Sample rate in samples per second
            file_name (string): name to save the file as (ex: 'MAOP_Tones')
        """
        frequency_spacings = [
            freq for freq in frequency_spacings
        ]  # convert to list with comma spacing
        arguments_string = args_to_csv_strings(
            [
                frequency_spacings,
                frequency_offset,
                sample_rate,
                self.WaveForm_folder_path + file_name,
            ]
        )
        multitone_command = "CreateMultitoneWaveform " + arguments_string
        self.send_command(multitone_command, receive=True)

    @setting(
        2927,
        "make weighted multitone text",
        frequency_spacings="*?",
        dBm_weights="*?",
        frequency_offset="v",
        sample_rate="v",
        file_name="s",
    )
    def make_weighted_multitone_text(
        self,
        c,
        frequency_spacings,
        dBm_weights,
        frequency_offset,
        sample_rate,
        file_name,
    ):
        """Sends a string command to the AWG Windows server that calls a function to write and save the
        desired multitone waveform as a text file.

        Args:
            frequency_spacings (list): list of frequencies (Hz) to include in the multitone signal
            frequency_offset (float): a single frequency to add to each frequency in 'frequency_spacings'
            sample_rate (float): Sample rate in samples per second
            file_name (string): name to save the file as (ex: 'MAOP_Tones')
        """
        frequency_spacings = [
            freq for freq in frequency_spacings
        ]  # convert to list with comma spacing
        dBm_weights = [
            dBm_weight for dBm_weight in dBm_weights
        ]  # convert to list with comma spacing
        arguments_string = args_to_csv_strings(
            [
                frequency_spacings,
                dBm_weights,
                frequency_offset,
                sample_rate,
                self.WaveForm_folder_path + file_name,
            ]
        )
        multitone_command = "CreateWeightedMultitoneWaveform " + arguments_string
        print(multitone_command)
        self.send_command(multitone_command, receive=True)

    @setting(5, "kill")
    def kill(self, c):
        """Breaks connection to the AWG windows server"""
        self.send_command("break")

    @setting(54, "reset")
    def reset_last_waveform(self, c):
        """Breaks connection to the AWG windows server"""
        self.send_command("reset ")

    @setting(55, "set timeout", timeout="v")
    def set_timeout(self, c, timeout=20):
        """Breaks connection to the AWG windows server"""
        self.socket_timeout = timeout
        self.server.settimeout(self.socket_timeout)


#################################
# MAOP_frequencies = [-9.450272e6,-3.162039e6,3.129963e6,9.425743e6] # frequency spacings to make multitone signal
# MAOP_frequency_offset = 2.5e9 # frequency offset to apply to all frequencies in multitone signal
# sample_rate = 16e9 # sample rate of AWG
# MAOP_file_name = 'MAOP_Tones' # file name of waveform text file that will be saved on the AWG computer
#
# AWG_Windows = AWG_windows_server(HOST,PORT,waveform_file_path)
# AWG_Windows.make_multitone_text(MAOP_frequencies,MAOP_frequency_offset,sample_rate,MAOP_file_name)

#################################


__server__ = AWG_Windows_Server()

if __name__ == "__main__":
    from labrad import util

    util.runServer(__server__)
