import matplotlib
import matplotlib.pyplot as plt
import numpy as np

episodes = 200
pTransfer = 0.3
alpha_TF = 0.5
secsPerDay = 46800

alpha_BR_start = 0.3
alpha_BR_end = 0.05

alpha_expFactor = np.log(alpha_BR_start/alpha_BR_end) #1.6

secsOfTF = pTransfer*episodes*secsPerDay
secsOfBR = (((1-pTransfer)*episodes)*secsPerDay)


y = np.array([])
globalSeconds = np.array([])

for day in range(episodes):
	for currSod in range(0, secsPerDay, 100):
		if day < pTransfer*episodes:
			y = np.append(y, alpha_TF)	
		else:
			totalSec = day*secsPerDay + currSod
			y = np.append(y, 
				alpha_BR_start*np.exp(-alpha_expFactor*(totalSec-secsOfTF)/secsOfBR) )

#	globalSeconds = np.append(globalSeconds, 
#		day*secsPerDay + np.double(np.arange(secsPerDay)))



#y = np.exp(-2.3*globalSeconds/(200*secsPerDay))

x = np.arange(len(y))
plt.plot(x, y)
plt.show()