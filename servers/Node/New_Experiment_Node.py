#!/usr/bin/env python
import labrad
from numpy import array
from time import sleep
#connect to LabRAD
try:
	cxn = labrad.connect()
except:
	print 'Please start LabRAD Manager'
	sleep(10)
	raise()

nodeDict = {
			'node_tony_dell':
				['Data Vault', 'Wiki Server'],
	}

for node in nodeDict.keys(): #sets the order of opening
	#make sure all node servers are up
	if not node in cxn.servers: print node + ' is not running'
	else:
		print '\n' + 'Working on ' + node + '\n'
		#if node server is up, start all possible servers on it that are not already running
		running_servers = array(cxn.servers[node].running_servers().asarray)
		for server in nodeDict[node]:
			if server in running_servers: 
				print server + ' is already running'
			else:
				print 'starting ' + server
				try:
					cxn.servers[node].start(server)
				except:
					print 'ERROR with ' + server


sleep(10)
