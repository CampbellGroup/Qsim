import labrad
import numpy as np
from pylab import *

plotnumber = 113
title = '369 Line Scan'


cxn = labrad.connect(name = 'plotting module')
dv = cxn.data_vault
dv.cd(['', '369 Wavemeter Line Scan'])
fig, ax = subplots()
dv.open(plotnumber)
params = dv.get_parameter('Solutions-0-Lorentzian')

amp = params[2]*60
FWHM = params[0]
gamma = 1e6*FWHM
center = params[1]*1e6
offset = params[3]

arr = dv.get().asarray
xpoints = 1e6*(arr[:,0] - params[1])*2

fit = amp*(gamma)/((xpoints)**2 + (gamma)**2) + offset

ax.plot(xpoints, arr[:,1], label = '369 data')
ax.plot(xpoints, fit)
f = center*2*1e-6
ax.text(-400, 16, 'Center Frequency = ' + str(float("{0:.6f}".format(f))) + 'THz', fontsize=15)
ax.set_xlabel('Frequency detuning from fit (MHz)')
ax.set_ylabel('Kilo Counts/sec')
ax.set_title(title)
legend()
show()
cxn.disconnect()
