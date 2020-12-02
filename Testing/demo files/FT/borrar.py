import pandas as pd
import numpy as np
import var
import matplotlib.pyplot as plt

def loadData():
    df=pd.DataFrame.from_csv('./data_org/dfQueue_testTF_int0_day0.csv')
    timeBase = df.values[:,0]*(1.0*var.secondsInHour)
    samples = df.shape[0]
    dataQueues = {}; dataTimes = {}; dataSpeed = {}
    for v in var.Vertex:
        edges = len(var.vertexAgents[v].listEdges)
        dataQueues[v] = np.zeros([samples, edges]) 
        dataTimes[v] = np.zeros([samples, edges]) 
        dataSpeed[v] = np.zeros([samples, edges]) 
    
        for day in range(var.totalDaysTest-1):
            df=pd.DataFrame.from_csv(f'./data_org/dfQueue_testTF_int{v}_day{day}.csv')
            dataQ = df.values
            df=pd.DataFrame.from_csv(f'./data_org/dfWaiting_testTF_int{v}_day{day}.csv')
            dataW = df.values
            df=pd.DataFrame.from_csv(f'./data_org/dfSpeed_testTF_int{v}_day{day}.csv')
            dataS = df.values
            for e in range(edges):
                dataQueues[v][:,e] += dataQ[:,e+1] #en veh
                dataTimes[v][:,e] += dataW[:,e+1] #en minutos
                dataSpeed[v][:,e] += dataS[:,e+1] #en m/s
    return timeBase, dataQueues, dataTimes, dataSpeed

timeBase, dataQueues, dataTimes, dataSpeed = loadData()
newData=np.random.randint(0,16,200)
avg_mask = np.ones(var.WINDOW) / var.WINDOW
qant = np.zeros(200) 
qnew = np.zeros(200)

for i in range(1,200):
	q = dataQueues[0][0:i,0] + newData[0:i]
	q = q/5.0
	qant[i] = q[-1]
	if i < var.WINDOW:
		qnew[i]= np.mean(qant[0:i])
	else:
		q = np.convolve(qant[0:i], avg_mask, 'same')
		q = np.mean(qant[i-var.WINDOW:i])
		qnew[i] = q

fig1, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)

ax1.plot(qant)
ax1.plot(qnew)


q1 = dataQueues[0][0:200,0] + newData[0:200]
q1 = q1/5.0
q2 = np.convolve(q1, avg_mask, 'same')
ax2.plot(q1)
ax2.plot(q2)
ax2.plot(qnew)
plt.show()

