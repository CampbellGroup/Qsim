from ConfigParser import SafeConfigParser

def load_default():
    config = SafeConfigParser()
    config.read('crystal_config.ini')
    
    try: 
        config.add_section('trap_parameters')
    except:
        pass
    
    config.set('trap_parameters', 'rnot', '512e-6')
    config.set('trap_parameters', 'Voltage', '200.0')
    config.set('trap_parameters', 'RF_frequency', '40e6')
    config.set('trap_parameters', 'mass', '2.89e-25')
    config.set('trap_parameters', 'assymetry', '1')
    
    try:
        config.add_section('simulation_parameters')
    except:
        pass
    
    config.set('simulation_parameters', 'step_size', '1e-6')
    config.set('simulation_parameters', 'iterations', '1200')
    config.set('simulation_parameters', 'init_random_spread', '20e-6')

    with open('crystal_config.ini', 'w') as f:
        config.write(f)

    
def print_trap_paramters():
    config = SafeConfigParser()
    config.read('crystal_config.ini')

    print config.get('trap_parameters', 'rnot') 
    print config.get('trap_parameters', 'Voltage') 
    print config.get('trap_parameters', 'RF_frequency')
    print config.get('trap_parameters', 'mass')
    print config.get('trap_parameters', 'assymetry')
        
def get_trap_paramters():
    config = SafeConfigParser()
    config.read('crystal_config.ini')

    rnot =  float(config.get('trap_parameters', 'rnot'))
    Voltage =  float(config.get('trap_parameters', 'Voltage'))
    RF_frequency =  float(config.get('trap_parameters', 'RF_frequency'))
    mass =  float(config.get('trap_parameters', 'mass'))
    assy =  float(config.get('trap_parameters', 'assymetry'))
    return [rnot, Voltage, RF_frequency, mass, assy]

def get_simulation_parameters():
    
    config = SafeConfigParser()
    config.read('crystal_config.ini')

    step_size =  float(config.get('simulation_parameters', 'step_size'))
    iters =  float(config.get('simulation_parameters', 'iterations'))
    spread =  float(config.get('simulation_parameters', 'init_random_spread'))
    return [step_size, iters, spread]

def set_voltage(volts):
    config = SafeConfigParser()
    config.read('crystal_config.ini')
    config.set('trap_parameters', 'Voltage', str(volts))
    with open('crystal_config.ini', 'w') as f:
        config.write(f)
        
def set_RF_frequency(freq):
    config = SafeConfigParser()
    config.read('crystal_config.ini')
    config.set('trap_parameters', 'RF_frequency', str(freq))
    with open('crystal_config.ini', 'w') as f:
        config.write(f)
        
def set_char_size(size):
    config = SafeConfigParser()
    config.read('crystal_config.ini')
    config.set('trap_parameters', 'rnot', str(size))
    with open('crystal_config.ini', 'w') as f:
        config.write(f)
        
def set_assymetry(assy):
    config = SafeConfigParser()
    config.read('crystal_config.ini')
    config.set('trap_parameters', 'assymetry', str(assy))
    with open('crystal_config.ini', 'w') as f:
        config.write(f)
        
def set_step_size(step):
    config = SafeConfigParser()
    config.read('crystal_config.ini')
    config.set('simulation_parameters', 'step_size', str(step))
    with open('crystal_config.ini', 'w') as f:
        config.write(f)
        
def set_iterations(iters):
    config = SafeConfigParser()
    config.read('crystal_config.ini')
    config.set('simulation_parameters', 'iterations', str(iters))
    with open('crystal_config.ini', 'w') as f:
        config.write(f)
        
def set_init_spread(spread):
    config = SafeConfigParser()
    config.read('crystal_config.ini')
    config.set('simulation_parameters', 'init_random_spread', str(spread))
    with open('crystal_config.ini', 'w') as f:
        config.write(f)
    