import os, sys
import subprocess
if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:   
	sys.exit("please declare environment variable 'SUMO_HOME'")
import traci
sumoBinary = "sumo-gui" #sumo-gui
import random
import time

sumoCmd = [sumoBinary, "-c", "../redSumo/bogota.sumo.cfg", "--no-step-log", "true"]
traci.start(sumoCmd) 

currSod = 0
agent_TLS = {}

tls = 'tls_14_45'
listJunctions = [7]
actionPhases = [0,1]
auxPhases = [[-1, [3,2,6]],
             [[5,2,4], -1]]
phases=[
    'GGGGrrrrGGGGrr',
    'rrrrGGGGrrrrGG',
    'rrrrrrrrrrrrrr',    
    'YYYYrrrrYYYYrr',
    'uuuurrrruuuurr',    
    'rrrrYYYYrrrrYY',
    'rrrruuuurrrruu' ]
timeYellow = 2
minTimeGreen = 9


lastAction = 0
currAction = 0
RedYellowGreenState = 'GGGGrrrrGGGGrr'
finishPhase = [-1, True]


def step():
	global currSod
	currSod += 1
	

def changeAction(action, currSod):
	global lastAction, currAction, finishPhase
	lastAction = currAction
	currAction = action
	finishPhase = [currSod, False]


def setPhase(currSod):
	global RedYellowGreenState, finishPhase
	aux_phase = auxPhases[lastAction][currAction]
	if(not(type(aux_phase)==list)):
		if aux_phase != -1:
			if currSod <= finishPhase[0]+timeYellow:
				RedYellowGreenState = phases[aux_phase]
			elif (currSod > finishPhase[0]+timeYellow) and (currSod <= finishPhase[0]+timeYellow+minTimeGreen):
				RedYellowGreenState = phases[currAction]
			else:
				finishPhase = [-1, True]
		else:
			RedYellowGreenState = phases[currAction]
			if currSod > (finishPhase[0]+minTimeGreen):
				finishPhase = [-1, True]
	else:
		if currSod <= finishPhase[0]+timeYellow:
			RedYellowGreenState = phases[aux_phase[0]]
		elif (currSod > finishPhase[0]+timeYellow) and (currSod <= finishPhase[0]+(2*timeYellow)):
			RedYellowGreenState = phases[aux_phase[1]]
		elif (currSod > finishPhase[0]+timeYellow) and (currSod <= finishPhase[0]+(3*timeYellow)):
			RedYellowGreenState = phases[aux_phase[2]]
		elif (currSod > finishPhase[0]+(3*timeYellow)) and (currSod <= finishPhase[0]+(3*timeYellow)+minTimeGreen):
			RedYellowGreenState = phases[currAction]
		else:
			finishPhase = [-1, True]


for i in range(0,100):
	step()
	if finishPhase[1]:
		action = input('new action')
		changeAction(int(action), currSod)
	setPhase(currSod)
	traci.trafficlight.setRedYellowGreenState(tls,RedYellowGreenState)
	traci.simulationStep()
	p_index = phases.index(RedYellowGreenState)	
	print('Sec: '+str(currSod) + '  last: '+str(lastAction) + '  curr:' + str(currAction)+ '  Phase: '+str(p_index))
	time.sleep(5)