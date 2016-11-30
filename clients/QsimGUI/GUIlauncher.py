from subprocess import call
check = call(["/home/qsimexpcontrol/.virtualenvs/labrad/bin/python2.7", "/home/qsimexpcontrol/LabRAD/Qsim/clients/QsimGUI/splash_checker.py"])
if check == 0:
	call(["/home/qsimexpcontrol/.virtualenvs/labrad/bin/python2.7", "/home/qsimexpcontrol/LabRAD/Qsim/clients/QsimGUI/QsimGUI2.0.py"])
