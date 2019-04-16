from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class shelving(pulse_sequence):

    required_parameters = [
                           ('Shelving', 'duration'),
                           ('Shelving', 'power'),
                           ('Shelving', 'assist_power'),
                           ('Shelving', 'repump_power'),
                           ('Shelving', 'freq_upper_ramp'),
                           ('Shelving', 'freq_lower_ramp'),
                           ('Transitions', 'main_cooling_369'),
                           ('DopplerCooling', 'detuning')
                           ]

    def sequence(self):
        p = self.parameters
        # shutterlag = U(8.0, 'ms')
        dt = U(2.0,'ms') # ramp length in ms
        N = p.Shelving.duration['ms']/dt['ms'] # number of ramps during a certain sub sequence
        dF = p.Shelving.freq_upper_ramp['MHz'] - p.Shelving.freq_lower_ramp['MHz']
        
        self.addDDS('369DP',
                    self.start,
                    p.Shelving.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
                    p.Shelving.assist_power)

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.Shelving.duration,
                    U(110.0, 'MHz'),
                    U(-20.8, 'dBm'))

        self.addDDS('935SP',
                    self.start,
                    p.Shelving.duration,
                    U(320.0, 'MHz'),
                    p.Shelving.repump_power)

        # sets the initial freq for time dt
        self.addDDS('411SP',
                    self.start,
                    dt,
                    U(250.0, 'MHz'),
                    p.Shelving.power)

        # does the first half ramp up in freq
        self.addDDS('411SP',
                    self.start + dt,
                    dt,
                    p.Shelving.freq_upper_ramp,
                    p.Shelving.power,
                    ramp_rate=U(p.Shelving.freq_upper_ramp['MHz']/1.0, 'MHz'))

        # ramps from freq_upper to freq_lower in time dt repeatedly throughout sequence
        for step in range(int((N-2)/2.0)):
            self.addDDS('411SP',
                        self.start + 2*(step+1)*dt,
                        dt,
                        p.Shelving.freq_lower_ramp,
                        p.Shelving.power,
                        ramp_rate=U(dF/dt, 'MHz'))

            self.addDDS('411SP',
                        self.start + (2*step+3)*dt,
                        dt,
                        p.Shelving.freq_upper_ramp,
                        p.Shelving.power,
                        ramp_rate=U(dF/dt, 'MHz'))

        self.addTTL('760TTL', self.start, p.Shelving.duration)
        self.end = self.start + p.Shelving.duration
