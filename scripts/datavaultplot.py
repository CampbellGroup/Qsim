import labrad
import numpy as np
from pylab import *


def dvplot(folder, num, title, xname, yname,labels):
	cxn = labrad.connect(name = 'plotting module')
	dv = cxn.data_vault
	dv.cd(['', folder])
	fig, ax = subplots()
	for i, item in enumerate(num):
		dv.open(item)
		arr = dv.get().asarray
		ax.plot(arr[:,0],arr[:,1], label = labels[i])
		ax.set_xlabel(xname)
		ax.set_ylabel(yname)
	ax.set_title(title)
	legend()
	show()


def backcount(num):
	for i in range(num):
		print (num - i)

	

