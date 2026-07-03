# -*- coding: utf-8 -*-

import labrad
from Qsim.scripts.pulse_sequences.microwave_point.microwave_ramsey_point import (
    MicrowaveRamseyPoint as sequence,
)
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np
from twisted.internet.defer import inlineCallbacks, returnValue


class MicrowaveRamseyExperiment(QsimExperiment):
    """
        Scan delay time between microwave pulses with variable pulse area

        Pulse sequence diagram:

    Standard:
        369SP            |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        DopplerCoolingSP |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        StateDetectionSP |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        OpticalPumpingSP |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        MicrowaveTTL     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█████▁▁▁▁▁▁▁▁▁█████▁▁▁▁▁▁▁▁▁▁▁▁
        Microwave_qubit  |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▓▓▓▓▓▁▁▁▁▁▁▁▁▁▓▓▓▓▓▁▁▁▁▁▁▁▁▁▁▁▁
        935SP/976SP      |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        760SP/760SP2     |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        ReadoutCount     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
             (TurnOffAll) DC          OP          RMI    ~~~~~~~~~     StandardSD

    FiberEOM:
        369SP            |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        SynthHD          |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        SynthNV          |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        MicrowaveTTL     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█████▁▁▁▁▁▁▁▁▁█████▁▁▁▁▁▁▁▁▁▁▁▁
        Microwave_qubit  |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▓▓▓▓▓▁▁▁▁▁▁▁▁▁▓▓▓▓▓▁▁▁▁▁▁▁▁▁▁▁▁
        935SP/976SP      |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        760SP/760SP2     |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        ReadoutCount     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
             (TurnOffAll) DC          OP          RMI    ~~~~~~~~~     StandardSD
    """

    name = "Microwave Ramsey Experiment"

    exp_parameters = []
    exp_parameters.append(("DopplerCooling", "detuning"))
    exp_parameters.append(("Transitions", "main_cooling_369"))
    exp_parameters.append(("MicrowaveInterrogation", "detuning"))
    exp_parameters.append(("MicrowaveInterrogation", "AWG_Channel"))
    exp_parameters.append(("MicrowaveInterrogation", "AWG_Channel_1_Power"))
    exp_parameters.append(("MicrowaveInterrogation", "AWG_Channel_2_Power"))
    exp_parameters.append(("MicrowaveInterrogation", "AC_line_trigger"))
    exp_parameters.append(("MicrowaveInterrogation", "delay_from_line_trigger"))
    exp_parameters.append(("MicrowaveRamsey", "delay_time"))
    exp_parameters.append(("MicrowaveRamsey", "fixed_delay_time"))
    exp_parameters.append(("MicrowaveRamsey", "detuning"))
    exp_parameters.append(("MicrowaveRamsey", "scan_type"))
    exp_parameters.append(("MicrowaveRamsey", "phase_scan"))
    exp_parameters.append(("MicrowaveInterrogation", "AC_line_trigger"))
    exp_parameters.append(("MicrowaveInterrogation", "delay_from_line_trigger"))
    exp_parameters.append(("Modes", "state_detection_mode"))
    exp_parameters.append(("ShelvingStateDetection", "repetitions"))
    exp_parameters.append(("StandardStateDetection", "repetitions"))
    exp_parameters.append(("StandardStateDetection", "points_per_histogram"))
    exp_parameters.append(("StandardStateDetection", "state_readout_threshold"))
    exp_parameters.append(("Shelving_Doppler_Cooling", "doppler_counts_threshold"))

    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(("EmptySequence", "duration"))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        #### 2/9/26 ###
        if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
            self.AWG_inst = self.cxn.awg_server  # connect to DAC server
            self.AWG_inst.select_device(0)
            self.AWG_windows = self.cxn.awg_windows_server
        ##############

    def run(self, cxn, context):
        # if self.p["MicrowaveInterrogation.AC_line_trigger"] == "On":
        #     self.pulser.line_trigger_state(True)
        #     self.pulser.line_trigger_duration(
        #         self.p["MicrowaveInterrogation.delay_from_line_trigger"]
        #     ) #4/8/26
        self.pulser.line_trigger_state(
            self.p["MicrowaveInterrogation.AC_line_trigger"] == "On"
        )
        self.pulser.line_trigger_duration(
            self.p["MicrowaveInterrogation.delay_from_line_trigger"]
        )
        scan_parameter = self.p["MicrowaveRamsey.scan_type"]
        mode = self.p["Modes.state_detection_mode"]

        self.p["MicrowaveInterrogation.detuning"] = self.p["MicrowaveRamsey.detuning"]

        #### 2/9/26 ###
        if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
            qubit = self.p["Line_Selection.qubit"]
            if qubit == "qubit_0":
                center = self.p["Transitions.qubit_0"]
            elif qubit == "qubit_plus":
                center = self.p["Transitions.qubit_plus"]
            elif qubit == "qubit_minus":
                center = self.p["Transitions.qubit_minus"]
            else:
                print(
                    "INPUT ERROR:\nLine_Selection.qubit must be a single qubit, otherwise use multitone Ramsey experiment"
                )

            freq = self.p["ddsDefaults.qubit_dds_freq"] - (
                self.p["MicrowaveInterrogation.detuning"] + center
            )
            channel = self.p["MicrowaveInterrogation.AWG_Channel"]
            AWG_power = self.p[
                "MicrowaveInterrogation.AWG_Channel_" + channel + "_Power"
            ]
            self.init_AWG(channel=channel, power=AWG_power)
            self.AWG_load_waveform(
                channel=channel, frequency=freq, waveform="HP_microwave"
            )
            self.AWG_play_signals()

        if scan_parameter == "delay_time":
            self.setup_datavault(
                "time", "probability"
            )  # gives the x and y names to Data Vault
            self.setup_grapher("Microwave Ramsey Experiment")
            self.dark_time = self.get_scan_list(self.p["MicrowaveRamsey.delay_time"], "ms")
            for i, dark_time in enumerate(self.dark_time):
                should_break = self.update_progress(i / float(len(self.dark_time)))
                if should_break:
                    break
                self.p["EmptySequence.duration"] = U(dark_time, "ms")
                self.program_pulser(sequence)
                if mode == "Shelving":
                    [doppler_counts, detection_counts] = self.run_sequence(
                        max_runs=500, num=2
                    )
                    errors = np.where(
                        doppler_counts
                        <= self.p["Shelving_Doppler_Cooling.doppler_counts_threshold"]
                    )
                    counts = np.delete(detection_counts, errors)
                else:
                    [counts] = self.run_sequence()
                if i % self.p["StandardStateDetection.points_per_histogram"] == 0:
                    hist = self.process_data(counts)
                    self.plot_hist(hist)
                pop = self.get_pop(counts)
                self.dv.add(dark_time, pop)

        elif scan_parameter == "phase":
            self.setup_datavault("phase", "probability")
            self.setup_grapher("Microwave Ramsey Experiment")
            self.phase_list = self.get_scan_list(
                self.p["MicrowaveRamsey.phase_scan"], "deg"
            )
            self.p["EmptySequence.duration"] = self.p["MicrowaveRamsey.fixed_delay_time"]
            print(str(self.p["MicrowaveRamsey.fixed_delay_time"]))
            for i, phase in enumerate(self.phase_list):
                should_break = self.update_progress(i / float(len(self.phase_list)))
                if should_break:
                    break
                self.p["MicrowaveInterrogation.microwave_phase"] = U(phase, "deg")
                self.program_pulser(sequence)
                if mode == "Shelving":
                    [doppler_counts, detection_counts] = self.run_sequence(
                        max_runs=500, num=2
                    )
                    errors = np.where(
                        doppler_counts
                        <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold
                    )
                    counts = np.delete(detection_counts, errors)
                else:
                    [counts] = self.run_sequence()
                if i % self.p.StandardStateDetection.points_per_histogram == 0:
                    hist = self.process_data(counts)
                    self.plot_hist(hist)
                pop = self.get_pop(counts)
                print(len(counts))
                print(str(phase) + " deg , " + str(pop) + "population")
                self.dv.add(phase, pop)

        if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
            self.AWG_play_signals(False)

    def finalize(self, cxn, context):
        self.pulser.line_trigger_state(False)
        self.pulser.line_trigger_duration(U(0.0, "us"))

    @inlineCallbacks
    def init_AWG(self, channel, power, other_channel_off=True):
        channel = int(channel)
        yield self.AWG_inst.change_amplitude(
            channel, power["dBm"]
        )  # change power of waveform
        yield self.AWG_inst.rf_channel_state(channel, True)
        if other_channel_off:
            yield self.AWG_inst.rf_channel_state(channel % 2 + 1, False)
        yield self.AWG_inst.channel_run_mode(channel, "Continuous")

    @inlineCallbacks
    def AWG_load_waveform(self, channel, frequency, waveform):
        channel = int(channel)
        yield self.AWG_windows.make_multitone_text(
            [0], frequency["Hz"], 16000000000, waveform
        )
        yield self.AWG_inst.text_to_waveform(waveform)
        yield self.AWG_inst.assign_waveform_to_channel(
            channel, waveform
        )  # load waveform to channel 1

    @inlineCallbacks
    def AWG_play_signals(self, play_state=True):
        yield self.AWG_inst.play_signals(play_state)


if __name__ == "__main__":
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveRamseyExperiment(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
