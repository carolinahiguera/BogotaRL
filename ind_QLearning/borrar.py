import os, sys
import subprocess
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:   
	sys.exit("please declare environment variable 'SUMO_HOME'")
import traci
sumoBinary = "sumo-gui" #sumo-gui

sumoCmd = [sumoBinary, "-c", "../redSumo/bogota.sumo.cfg", "--no-step-log", "true"]
traci.start(sumoCmd) 