from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence

class doppler_cooling(pulse_sequence):

    required_parameters = [
                           ('DopplerCooling', 'power'),
                           ('DopplerCooling', 'detuning'),
                           ('DopplerCooling', 'duration'),
                           ('Transitions', 'main_cooling_369')
                           ]

    def sequence(self):
        p = self.parameters
        self.addDDS('369',
                    self.start,
                    p.DopplerCooling.duration,
                    p.Transitions.main_cooling_369 + p.DopplerCooling.detuning,
                    p.DopplerCooling.power)

        self.end = self.start + p.DopplerCooling.duration
