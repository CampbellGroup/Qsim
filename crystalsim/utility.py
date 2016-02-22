import numpy as np
import matplotlib.pyplot as plt

from settings import settings
import constants
settings = settings()

def get_potential_coefficient(mass=settings.m, RF_freq = settings.RF_freq, 
                              V = settings.V, rnot = settings.rnot, q = constants.q ):
    omegaRF = 2 * np.pi * RF_freq
    A = q**2 * V**2/(mass * omegaRF**2 * rnot**4)
    return A
        
def get_secular_freq_Hz(self, mass = settings.m):
    A = get_potential_coefficient(mass=mass)
    wsec = np.sqrt(2*A/mass)
    f = wsec/(2 * np.pi)
    return f
    
def ion_distance(ion1, ion2):
    d = np.sqrt((ion1.x - ion2.x)**2 + (ion1.y - ion2.y)**2)
    return d

def interaction_energy(particle, otherions):
    Eint = 0
    for otherion in otherions:
        x_sep = otherion.x - particle.x
        y_sep = otherion.y - particle.y
        d = np.sqrt(x_sep**2 + y_sep**2)
        Eint += constants.q**2/(4 * np.pi * constants.epsilon * d)
    return  Eint

def pos_energy(particle, assy = 1):
    A = get_potential_coefficient()
    pos_E =  A * (assy * particle.x**2 + particle.y**2/assy ) 
    return pos_E

def total_energy(ions, assy):
    E_tot = 0
    for i, particle in enumerate(ions):
        otherions =  ions[i+1 :] #ions[:i] + ions[i+1 :] for half the interaction energy
        E_tot += interaction_energy(particle, otherions)
        E_tot += pos_energy(particle, assy)
    return E_tot

def plot_ions(ions, initial = False):
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    x = []
    y = []
    color = []

    if initial:
        for particle in ions:
            x.append(particle.x0 * 1e6)
            y.append(particle.y0 * 1e6) 
            color.append(particle.color)       
    else:
        for particle in ions:
            x.append(particle.x * 1e6)
            y.append(particle.y * 1e6)
            color.append(particle.color) 
            
    ax.axis('equal')
    ax.scatter(x,y, c= color)  
        
    plt.show()
    return fig
        
    
def fit_frequency(disty, prof):
    newx = (disty[0] - disty[0][np.argmin(prof)])
    newy = prof - np.min(prof)
    a = np.polyfit(newx,newy,2)
    plt.plot(newx,newy, newx, a[0]*newx**2)
    f = np.sqrt(2*a[0]/(settings.m))/2/np.pi
    return f
    