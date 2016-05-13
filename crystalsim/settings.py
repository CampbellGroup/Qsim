from ConfigParser import SafeConfigParser
import os
import time
path = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(path, 'crystal_config.ini')

trap_params = ['rnot', 'Voltage', 'RF_frequency', 'mass', 'assymetry']
trap_defaults = ['512e-6', '200', '40e6', '2.89e-25', '1']

sim_params = ['step_size', 'iterations', 'init_random_spread']
sim_defaults = ['1e-6', '1200', '20e-6']


def load_default_trap_parameters():
    for i, param in enumerate(trap_params):
        write_config('trap_parameters', param, trap_defaults[i])


def load_default_sim_parameters():
    for i, param in enumerate(sim_params):
        write_config('simulation_parameters', param, sim_defaults[i])


def print_trap_parameters():

    for param in trap_params:
        print read_config('trap_parameters', param) 


def get_trap_parameters():
    config = SafeConfigParser()
    config.read(config_file)

    try:
        rnot = float(config.get('trap_parameters', 'rnot'))
        Voltage = float(config.get('trap_parameters', 'Voltage'))
        RF_frequency = float(config.get('trap_parameters', 'RF_frequency'))
        mass = float(config.get('trap_parameters', 'mass'))
        assy = float(config.get('trap_parameters', 'assymetry'))
        return [rnot, Voltage, RF_frequency, mass, assy]
    except:
        print 'Invalid or missing parameters, \n Loading default parameters...'
        load_default_trap_parameters()
        config = SafeConfigParser()
        config.read(config_file)
        time.sleep(2)
        rnot = float(config.get('trap_parameters', 'rnot'))
        Voltage = float(config.get('trap_parameters', 'Voltage'))
        RF_frequency = float(config.get('trap_parameters', 'RF_frequency'))
        mass = float(config.get('trap_parameters', 'mass'))
        assy = float(config.get('trap_parameters', 'assymetry'))
        return [rnot, Voltage, RF_frequency, mass, assy]


def get_simulation_parameters():
    config = SafeConfigParser()
    config.read(config_file)

    try:
        step_size = float(config.get('simulation_parameters', 'step_size'))
        iters = float(config.get('simulation_parameters', 'iterations'))
        spread = float(config.get('simulation_parameters',
                                  'init_random_spread'))
        return [step_size, iters, spread]
    except:
        print 'Invalid or missing parameter, \n Loading default parameters...'
        load_default_sim_parameters()
        time.sleep(2)
        config = SafeConfigParser()
        config.read(config_file)
        step_size = float(config.get('simulation_parameters', 'step_size'))
        iters = float(config.get('simulation_parameters', 'iterations'))
        spread = float(config.get('simulation_parameters',
                                  'init_random_spread'))
        return [step_size, iters, spread]


def set_voltage(volts):
    write_config('trap_parameters', 'Voltage', str(volts))


def set_length_scale(rnot):
    write_config('trap_parameters', 'rnot', str(rnot))


def set_RF_frequency(freq):
    write_config('trap_parameters', 'RF_frequency', str(freq))


def set_char_size(size):
    write_config('trap_parameters', 'rnot', str(size))


def set_assymetry(assy):
    write_config('trap_parameters', 'assymetry', str(assy))


def set_step_size(step):
    write_config('simulation_parameters', 'step_size', str(step))


def set_iterations(iters):
    write_config('simulation_parameters', 'iterations', str(iters))


def set_init_spread(spread):
    write_config('simulation_parameters', 'init_random_spread', str(spread))


def write_config(category, key, value):
    config = SafeConfigParser()
    config.read(config_file)

    try:
        config.add_section(category)
    except:
        pass

    try:
        config.set(category, key, value)
        with open(config_file, 'w') as f:
            config.write(f)
    except IOError:
        print 'Could not write to config file '


def read_config(category, key):
    config = SafeConfigParser()
    config.read(config_file)
    try:
        return config.get('trap_parameters', 'rnot')
    except:
        print 'Could not find key'
