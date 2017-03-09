from objects import ion
from utility import total_energy
from progressbar import ProgressBar
from crystalconfigurations import symmetric_6
from settings import get_trap_parameters
from settings import get_simulation_parameters

import numpy as np
import matplotlib.pyplot as plt
import os
import datetime
import utility


def make_crystal(N_ions=6, starting_ions=None, constant_ion=None,
                 progress=True, assymetry=None):
    '''
    This function iterates random steps in postion and recalculates the energy
    of the configuration of N ions, if the energy is decreased it accepts
    the move and repeats
    '''

    A = utility.get_potential_coefficient()
    tp = get_trap_parameters()
    sp = get_simulation_parameters()

    if assymetry:
        assy = assymetry
    else:
        assy = tp[4]
    pos_spread = sp[2]
    iterations = sp[1]
    step_size = sp[0]

    if progress:
        p = ProgressBar(iterations)
    N = N_ions
    ions = []
    if starting_ions is None:
        for _i in range(N):
            # initiate ions in random position
            x0 = (np.random.rand() - 0.5)*pos_spread
            y0 = (np.random.rand() - 0.5)*pos_spread
            ions.append(ion(x0, y0))
    else:
        # initiate ions in specified starting positions
        for starting_ion in starting_ions:
            ions.append(ion(starting_ion.x, starting_ion.y,
                            starting_ion.color))
    E0 = total_energy(ions, assy)

    iters = 0
    E = [E0]
    last_E = E0
    if constant_ion is not None:
        for fixed in constant_ion:
            ions[fixed].constant = True
    while iters < iterations:
        if progress:
            p.animate(iters)
        iters += 1
        for particle in ions:
            if not particle.constant:  # Checks if ion is movable
                particle.lastx = particle.x
                particle.x = particle.x + (np.random.rand() - 0.5)*step_size
                particle.lasty = particle.y
                particle.y = particle.y + (np.random.rand() - 0.5)*step_size
                tot_E = total_energy(ions, assy, A)
                if tot_E < last_E:  # Check to take the position step or not
                    E.append(tot_E)
                    last_E = tot_E
                else:
                    particle.x = particle.lastx
                    particle.y = particle.lasty
    return E[-1], ions


def squeeze_crystal(starting_ions=None, max_assy=1.3, N_ions=6, steps = 100):

    timestamp = str(datetime.datetime.now())

    if starting_ions:
        prev_ions = starting_ions
    else:
        prev_ions = None

    assy_step = (max_assy - 1)/steps
    path = str(N_ions) + '_Ions/' + timestamp + '/'
    if not os.path.isdir(path):
        os.makedirs(path)
    plt.ion()
    xlims = [-40, 40]
    ylims = [-30, 30]

    x = []
    y = []
    color = []

    _E, ions = make_crystal(N_ions=N_ions, starting_ions=prev_ions,
                            progress=False)

    for ion in ions:
        color.append(ion.color)

    prev_ions = ions
    Eprofile = []
    assyprof = []
    for i in range(steps):
        assymetry = 1 + i*assy_step
	assyprof.append(assymetry)
        _E, ions = make_crystal(N_ions=N_ions, starting_ions=prev_ions,
                                progress=False, assymetry=assymetry)
	Eprofile.append(_E)
        prev_ions = ions
        x = []
        y = []
        for particle in ions:
            x.append(particle.x * 1e6)
            y.append(particle.y * 1e6)

        plt.clf()
        plt.xlim(xlims)
        plt.ylim(ylims)
        plt.text(0, 0, str(assymetry))
        plt.scatter(x, y, c=color)
        plt.pause(0.0001)
    return [assyprof, Eprofile]


def drag_ion(crystal = symmetric_6(6e-6), pinned_ions = [0], initpos = [(0,0)], finalpos = [(0,6e-6)], 
             steps = 200):

    plt.ion()
    xlims = [-40,40]
    ylims = [-30,30]
    
    N = len(crystal)
    ions = []
    Eprofile = []
    xsteps = []
    ysteps = []
    color = []
    
    for ion in crystal:
        color.append(ion.color)
        
    
    for ion in pinned_ions:
        xsteps.append([])
        ysteps.append([])

    for i, pos in enumerate(initpos):
        xsteps[i] = np.linspace(pos[0], finalpos[i][0],steps)
        ysteps[i] = np.linspace(pos[1], finalpos[i][1],steps)
        
    for i in range(steps):
        for j in range(len(pinned_ions)):
            crystal[j].x = xsteps[j][i]
            crystal[j].y = ysteps[j][i]
        E, ions = make_crystal(N_ions = N, starting_ions = crystal, constant_ion=pinned_ions, progress = False)
        Eprofile.append(E)
        x=[]
        y=[]
        for particle in ions:
            x.append(particle.x * 1e6)
            y.append(particle.y * 1e6)
        plt.clf()
        plt.xlim(xlims)
        plt.ylim(ylims)
        plt.scatter(x,y, c = color)
        plt.pause(0.0001)
    return [xsteps, ysteps], np.array(Eprofile)
