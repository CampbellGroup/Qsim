from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence


class doppler_cooling(pulse_sequence):

    required_parameters = [
                           ('DopplerCooling', 'doppler_cooling_power'),
                           ('DopplerCooling', 'doppler_cooling_frequency'),
                           ('DopplerCooling', 'doppler_cooling_duration'),
                           ]

    def sequence(self):
        p = self.parameters.DopplerCooling
        self.addDDS('369',
                    self.start,
                    p.doppler_cooling_duration,
                    p.doppler_cooling_frequency,
                    p.doppler_cooling_power)

        self.end = self.start + p.doppler_cooling_duration
