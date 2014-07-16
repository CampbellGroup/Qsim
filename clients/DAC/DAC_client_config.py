class DAC_config(object):
    '''
    configuration file for DAC client
    info is the configuration dictionary in the form
    {channel_name: (dac, channel (display_location)) }
    '''
    info = {'GND1    ': ((1, 1), (0,1)),
            'GND2    ': ((1, 2), (0,2)),
            'RFBIAS1': ((2, 1), (0,3)),
            'RFBIAS2': ((2, 2), (0,4))
            }