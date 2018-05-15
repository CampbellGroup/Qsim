class drift_tracker_config(object):
    '''
    drift tracker configuration file

    Attributes
    ----------
    info: dict
    {Grapher Tab: (Server, function, arguments)}
    '''
    info = {
            'Drift Tracker': ('Multipole Server', 'get_multipoles', None)
            }
