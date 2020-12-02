import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd 
import var
import numpy as np
exec(open("var.py").read())
path_ft = '/home/carolina/Documents/BogotaRL/fixed_time_org/csv_files/'
path_br = '/home/carolina/Documents/BogotaRL/br_marl/csv_files_test_t3/'
path_br2 = '/home/carolina/Documents/BogotaRL/br_marl/csv_files_train_t3/'
path_save = '/home/carolina/Documents/BogotaRL/results/'


avg_queues_junctions = None
avg_waitTimes_junctions = None
mean_reward_tls = None
# for tls in var.agent_TLS.keys():
# 	mean_reward_tls[tls] = np.zeros(var.episodes)

def ini_dataframes():
	global avg_queues_junctions, avg_waitTimes_junctions, mean_reward_tls
	cols = 5
	rows = 0
	for j in var.junctions.keys():
		rows += len(var.junctions[j].edges)
	avg_queues_junctions = pd.DataFrame(index=range(rows), columns=range(cols))
	avg_waitTimes_junctions = pd.DataFrame(index=range(rows), columns=range(cols))
	aux = ['junction', 'edge', '6-8', '8-15', '15-20']
	avg_queues_junctions.columns = aux
	avg_waitTimes_junctions.columns = aux
	rows = var.episodes
	cols = len(var.agent_TLS.keys())
	mean_reward_tls = pd.DataFrame(index=range(rows), columns=range(cols))
	mean_reward_tls.columns = list(var.agent_TLS.keys())


def get_avg_queues(method):
	global avg_queues_junctions, path_ft, path_br
	ini_dataframes()
	if method == 'ft':
		row = 0	
		for j in var.junctions.keys():
			queues_avg = pd.read_csv(path_ft + 'ft_queues_' + var.junctions[j].name + '_day' + str(0) + '.csv') 
			for day in range(1,var.days2Observe):
				queues_avg += pd.read_csv(path_ft+'ft_queues_' + var.junctions[j].name + '_day' + str(day) + '.csv') 
			queues_avg /= float(var.days2Observe)
			auxQ = [j] 
			for edge in var.junctions[j].edges:					
				q = 0
				auxQ.append(edge)
				for i in range(0,2*3600):
					q += queues_avg[edge][i]
				auxQ.append(q/float(i))
				#avg_queues_junctions[j][edge]['6-8'] = q/float(i)
				q = 0
				for i in range(2*3600,9*3600):
					q += queues_avg[edge][i]
				auxQ.append(q/float(i))
				#avg_queues_junctions[j][edge]['8-15'] = q/float(i)
				q = 0
				for i in range(9*3600,var.secondsInDay-1):
					q += queues_avg[edge][i]
				auxQ.append(q/float(i))
				#avg_queues_junctions[j][edge]['15-20'] = q/float(i)
				avg_queues_junctions.loc[row] = np.array([auxQ])
				row += 1
				auxQ = [j]				
		avg_queues_junctions.to_csv(path_save+'ft_queues.csv')
	elif method == 'br':
		row = 0	
		for j in var.junctions.keys():
			queues_avg = pd.read_csv(path_br + 'br_queues_' + var.junctions[j].name + '_day' + str(0) + '.csv') 
			for day in range(1,var.days2Observe):
				queues_avg += pd.read_csv(path_br+'br_queues_' + var.junctions[j].name + '_day' + str(day) + '.csv') 
			queues_avg = queues_avg/float(var.days2Observe)
			auxQ = [var.junctions[j].name] 
			for edge in var.junctions[j].edges:					
				q = 0
				auxQ.append(edge)
				for i in range(0,int((2*3600)/var.sampleTime)):
					q += queues_avg[edge][i]
				auxQ.append(q/float(i))
				#avg_queues_junctions[j][edge]['6-8'] = q/float(i)
				q = 0
				for i in range(int((2*3600)/var.sampleTime),int((9*3600)/var.sampleTime)):
					q += queues_avg[edge][i]
				auxQ.append(q/float(i))
				#avg_queues_junctions[j][edge]['8-15'] = q/float(i)
				q = 0
				for i in range(int((9*3600)/var.sampleTime),int((var.secondsInDay-1)/var.sampleTime)):
					q += queues_avg[edge][i]
				auxQ.append(q/float(i))
				#avg_queues_junctions[j][edge]['15-20'] = q/float(i)
				avg_queues_junctions.loc[row] = np.array([auxQ])
				row += 1
				auxQ = [var.junctions[j].name]
		avg_queues_junctions.to_csv(path_save+'br_queues.csv')
	else:
		print('ERROR: method not recognized')

def get_avg_waitTimes(method):
	global avg_waitTimes_junctions, path_ft, path_br
	ini_dataframes()
	if method == 'ft':
		row = 0	
		for j in var.junctions.keys():
			waitTimes_avg = pd.read_csv(path_ft + 'ft_times_' + var.junctions[j].name + '_day' + str(0) + '.csv') 
			for day in range(1,var.days2Observe):
				waitTimes_avg += pd.read_csv(path_ft+'ft_times_' + var.junctions[j].name + '_day' + str(day) + '.csv') 
			waitTimes_avg /= float(var.days2Observe)
			auxQ = [j] 
			for edge in var.junctions[j].edges:					
				q = 0
				auxQ.append(edge)
				for i in range(0,2*3600):
					q += waitTimes_avg[edge][i]
				auxQ.append(q/float(i))
				#avg_queues_junctions[j][edge]['6-8'] = q/float(i)
				q = 0
				for i in range(2*3600,9*3600):
					q += waitTimes_avg[edge][i]
				auxQ.append(q/float(i))
				#avg_queues_junctions[j][edge]['8-15'] = q/float(i)
				q = 0
				for i in range(9*3600,var.secondsInDay-1):
					q += waitTimes_avg[edge][i]
				auxQ.append(q/float(i))
				#avg_queues_junctions[j][edge]['15-20'] = q/float(i)
				avg_waitTimes_junctions.loc[row] = np.array([auxQ])
				row += 1
				auxQ = [j]				
		avg_waitTimes_junctions.to_csv(path_save+'ft_waitTimes.csv')
	elif method == 'br':
		row = 0	
		for j in var.junctions.keys():
			waitTimes_avg = pd.read_csv(path_br + 'br_times_' + var.junctions[j].name + '_day' + str(0) + '.csv') 
			for day in range(1,var.days2Observe):
				waitTimes_avg += pd.read_csv(path_br+'br_times_' + var.junctions[j].name + '_day' + str(day) + '.csv') 
			waitTimes_avg = waitTimes_avg/float(var.days2Observe)
			auxQ = [var.junctions[j].name] 
			for edge in var.junctions[j].edges:					
				q = 0
				auxQ.append(edge)
				for i in range(0,int((2*3600)/var.sampleTime)):
					q += waitTimes_avg[edge][i]
				auxQ.append(q/float(i))
				#avg_queues_junctions[j][edge]['6-8'] = q/float(i)
				q = 0
				for i in range(int((2*3600)/var.sampleTime),int((9*3600)/var.sampleTime)):
					q += waitTimes_avg[edge][i]
				auxQ.append(q/float(i))
				#avg_queues_junctions[j][edge]['8-15'] = q/float(i)
				q = 0
				for i in range(int((9*3600)/var.sampleTime),int((var.secondsInDay-1)/var.sampleTime)):
					q += waitTimes_avg[edge][i]
				auxQ.append(q/float(i))
				#avg_queues_junctions[j][edge]['15-20'] = q/float(i)
				avg_waitTimes_junctions.loc[row] = np.array([auxQ])
				row += 1
				auxQ = [var.junctions[j].name]
		avg_waitTimes_junctions.to_csv(path_save+'br_waitTimes.csv')
	else:
		print('ERROR: method not recognized')



def get_reward(method):
	global mean_reward_tls, path_br2, path_ft
	ini_dataframes()
	if method == 'br':
		for day in range(0,var.episodes):
			aux = []
			for tls in var.agent_TLS.keys():					
				df = pd.read_csv(path_br2+'br_rewards_' + str(tls) + '_day' + str(day) + '.csv')
				r = df.values[:,2]			
				aux.append(np.mean(r))
			mean_reward_tls.loc[day] = np.array([aux])
		mean_reward_tls.to_csv(path_save+'br_rewards.csv')
	elif method == 'ft':
		for day in range(0,var.days2Observe):
			aux = []
			for tls in var.agent_TLS.keys():					
				df = pd.read_csv(path_ft+'ft_rewards_' + str(tls) + '_day' + str(day) + '.csv')
				r = df.values[:,2]			
				aux.append(np.mean(r))
			mean_reward_tls.loc[day] = np.array([aux])
		mean_reward_tls.to_csv(path_save+'ft_rewards.csv')
	else:
		print('ERROR: method not recognized')


def plot_queues(j):
	path = '/home/carolina/Documents/BogotaRL/br_marl/csv_files_test_t3/'
	figsize = (15, 10)
	cols = 3
	gs = gridspec.GridSpec(len(var.junctions[j].edges) // cols + 1, cols)
	gs.update(hspace=0.4)
	queues_avg = pd.read_csv(path+'br_queues_' + var.junctions[j].name + '_day' + str(0) + '.csv') 
	t = queues_avg['currSod']
	for day in range(1,var.days2Observe):
		queues_avg += pd.read_csv(path+'br_queues_' + var.junctions[j].name + '_day' + str(day) + '.csv') 
	queues_avg = queues_avg/float(var.days2Observe)
	fig1 = plt.figure(num=1, figsize=figsize)
	ax = []
	for i, edge in enumerate(var.junctions[j].edges):
		row = (i // cols)
		col = i % cols
		ax.append(fig1.add_subplot(gs[row, col]))
		ax[-1].set_title(edge)
		ax[-1].plot(t, queues_avg[edge]) 
	plt.show()

def plot_waitTimes(j):
	path = '/home/carolina/Documents/BogotaRL/br_marl/csv_files_test_t3/'
	figsize = (15, 10)
	cols = 2
	gs = gridspec.GridSpec(len(var.junctions[j].edges) // cols + 1, cols)
	gs.update(hspace=0.4)
	times_avg = pd.read_csv(path+'br_times_' + var.junctions[j].name + '_day' + str(0) + '.csv') 
	t = times_avg['currSod']
	for day in range(1,var.days2Observe):
		times_avg += pd.read_csv(path+'br_times_' + var.junctions[j].name + '_day' + str(day) + '.csv') 
	times_avg = times_avg/float(var.days2Observe)
	fig1 = plt.figure(num=1, figsize=figsize)
	ax = []
	for i, edge in enumerate(var.junctions[j].edges):
		row = (i // cols)
		col = i % cols
		ax.append(fig1.add_subplot(gs[row, col]))
		ax[-1].set_title(edge)
		ax[-1].plot(t, times_avg[edge]) 
	plt.show()

def plot_reward():
	figsize = (15, 10)
	cols = 2
	gs = gridspec.GridSpec(len(var.agent_TLS.keys()) // cols + 1, cols)
	gs.update(hspace=0.4)	
	t = np.linspace(0,var.episodes-1,var.episodes)	
	fig1 = plt.figure(num=1, figsize=figsize)
	ax = []
	for i, tls in enumerate(var.agent_TLS.keys()):
		row = (i // cols)
		col = i % cols
		ax.append(fig1.add_subplot(gs[row, col]))
		ax[-1].set_title(tls)
		ax[-1].plot(t, mean_reward_tls[tls]) 
	plt.show()


	# plt.plot(mean_reward_tls[tls])
	# plt.show()
	# figsize = (15, 10)
	# cols = 1
	# gs = gridspec.GridSpec(1,cols)
	# gs.update(hspace=0.4)
	# fig1 = plt.figure(num=1, figsize=figsize)
	# ax = []
	# ax.append(fig1.add_subplot(gs[1, cols]))
	# t = np.linspace(0,var.episodes-1,var.episodes)
	# ax[-1].plot(t, mean_reward_tls[tls]) 
	# plt.show()