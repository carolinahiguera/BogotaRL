import pandas as pd
import numpy as np

tls = 'tls_7_45'
neighbors = ['tls_13_45', 'tls_7_46']
actionPhases = [0,1]
jointActions = list(itertools.product(actionPhases, actionPhases))

QValues = {}
M = {}
for nb in neighbors:
	QValues[nb]=None
	M[nb] = None

for nb in neighbors:
	df = pd.read_csv('QValues_' +tls +'_' + nb + '_day' + str(199) +'.csv')
	QValues[nb]=df.values
	df = pd.read_csv('M_' +tls +'_' + nb + '_day' + str(199) +'.csv')
	M[nb]=df.values


def get_action(s):
	QM = np.zeros([len(actionPhases)])
	for act_i in actionPhases:
		for nb in neighbors:			
			for act_j in actionPhases:
				aij = self.jointActions[nb].index((act_i, act_j))
				QM[act_i] += QValues[nb][s,aij] * M[nb][s,act_j]
	return QM	

