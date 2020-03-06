import labrad
import numpy as np
from pylab import *
from scipy.optimize import leastsq

plotnumber = 16
title = '935 Line Scan'

def lorentz(p,x):
    gamma = p[0] 
    xnot = p[1] 
    offset = p[2]
    height = p[3]
    P = height/((x-xnot)**2 + gamma**2) + offset
    return P

def errfunc(p, x, y):
    return y-lorentz(p,x)


cxn = labrad.connect(name = 'plotting module')
dv = cxn.data_vault
dv.cd(['', '935 Wavemeter Line Scan'])
fig, ax = subplots()
dv.open(plotnumber)

arr = dv.get().asarray
xpoints = (arr[:,0])*2
ypoints = arr[:,1]

# initguess = [gamma, vnot, offset]

initguess = np.array([41e6, 405.645745e12, 6.8, 20], dtype=np.double) #Initial guess
fit = leastsq(errfunc, initguess, args=(xpoints,ypoints))
print fit[0]
#ax.plot(xpoints, ypoints, label = '935 data')
ax.plot(xpoints, lorentz(fit[0],xpoints))
#ax.text(-400, 16, 'Center Frequency = ' + str(float("{0:.6f}".format(f))) + 'THz', fontsize=15)
ax.set_xlabel('Frequency detuning from fit (MHz)')
ax.set_ylabel('Kilo Counts/sec')
ax.set_title(title)
legend()
show()
cxn.disconnect()