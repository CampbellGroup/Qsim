class multiplexer_config(object):
    '''
    configuration file for multiplexer client
    info is the configuration dictionary in the form
    {channel_name: (port, hint, display_location, stretched))} Note: (0,0) location reserved for lock switch
    '''
    info = {'Channel 5': (5, '405.645680', (1,1), False),
            'Channel 6': (6, '320.571975', (1,2), False),
            'Channel 7': (7, '751.526150', (1,3), False)
            }
