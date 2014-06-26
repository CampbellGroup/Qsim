class DAC_config(object):
    '''
    configuration file for DAC client
    info is the configuration dictionary in the form
    {channel_name: (port, (display_location)) }
    '''
    info = {'GND1   ': (9, (0,1)),
            'GND2   ': (8, (0,2)),
            'RFBIAS1': (7, (0,3)),
            'RFBIAS2': (6, (0,4))
            }