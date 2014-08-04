class DAC_config(object):
    '''
    configuration file for DAC client
    info is the configuration dictionary in the form
    {Device_name: [Device ID, Channel 1 Name, Channel 2 Name, (Position 1), (Position 2), context = None] }
    '''
    info = {'RIGOL 1': [2, ('RF BIAS 1', 'RF BIAS 2'), (0, 0), (0,1), None],
            'RIGOL 2': [1, ('DC BIAS 1', 'DC BIAS 2'), (0, 2), (0,3), None]
            }