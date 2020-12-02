import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd 
import var
import numpy as np
exec(open("var.py").read())
path_ft = '/home/carolina/Documents/BogotaRL/fixed_time_org/csv_files'
path_br = '/home/carolina/Documents/BogotaRL/br_marl/csv_files_train_t3/'


avg_queues_junctions = {}
avg_waitTimes_junctions = {}
mean_reward_tls = {}
for tls in var.agent_TLS.keys():
	mean_reward_tls[tls] = np.zeros(var.episodes)

def get_avg_queues():
	global avg_queues_junctions
	
	for j in var.junctions.keys():
		queues_avg = pd.read_csv(path+'ft_queues_' + var.junctions[j].name + '_day' + str(0) + '.csv') 
		for day in range(1,var.episodes):
			queues_avg += pd.read_csv(path+'ft_queues_' + var.junctions[j].name + '_day' + str(day) + '.csv') 
		print('avg')
		queues_avg /= float(var.episodes)
		avg_queues_junctions[j] = {}
		for edge in var.junctions[j].edges:		
			avg_queues_junctions[j][edge] = {}
			q = 0
			for i in range(0,2*3600):
				q += queues_avg[edge][i]
			avg_queues_junctions[j][edge]['6-8'] = q/float(i)
			q = 0
			for i in range(2*3600,9*3600):
				q += queues_avg[edge][i]
			avg_queues_junctions[j][edge]['8-15'] = q/float(i)
			q = 0
			for i in range(9*3600,var.secondsInDay-1):
				q += queues_avg[edge][i]
			avg_queues_junctions[j][edge]['15-20'] = q/float(i)

def get_avg_waitTimes():
	global avg_waitTimes_junctions
	path = '/home/carolina/Documents/BogotaRL/br_marl/csv_files_train_t3/'
	for j in var.junctions.keys():
		times_avg = pd.read_csv(path+'ft_times_' + var.junctions[j].name + '_day' + str(0) + '.csv') 
		for day in range(1,var.episodes):
			times_avg += pd.read_csv(path+'ft_times_' + var.junctions[j].name + '_day' + str(day) + '.csv') 
		times_avg /= float(var.episodes)
		avg_waitTimes_junctions[j] = {}
		for edge in var.junctions[j].edges:		
			avg_waitTimes_junctions[j][edge] = {}
			q = 0
			for i in range(0,2*3600):
				q += times_avg[edge][i]
			avg_waitTimes_junctions[j][edge]['6-8'] = q/float(i)
			q = 0
			for i in range(2*3600,9*3600):
				q += times_avg[edge][i]
			avg_waitTimes_junctions[j][edge]['8-15'] = q/float(i)
			q = 0
			for i in range(9*3600,var.secondsInDay):
				q += times_avg[edge][i]
			avg_waitTimes_junctions[j][edge]['15-20'] = q/float(i)

def get_reward():
	global mean_reward_tls
	path = '/home/carolina/Documents/BogotaRL/br_marl/csv_files_train_t3/'
	for day in range(0,var.episodes):
		for tls in var.agent_TLS.keys():
			df = pd.read_csv(path+'br_rewards_' + str(tls) + '_day' + str(day) + '.csv')
			r = df.values[:,2]
			lrews = r[len(r)-50:-1]
			mean_reward_tls[tls][day] = np.mean(r)


def plot_queues(j):
	path = '/home/carolina/Documents/BogotaRL/br_marl/csv_files_train_t3/'
	figsize = (15, 10)
	cols = 3
	gs = gridspec.GridSpec(len(var.junctions[j].edges) // cols + 1, cols)
	gs.update(hspace=0.4)
	queues_avg = pd.read_csv(path+'br_queues_' + var.junctions[j].name + '_day' + str(0) + '.csv') 
	t = queues_avg['currSod']
	for day in range(1,var.episodes):
		queues_avg += pd.read_csv(path+'br_queues_' + var.junctions[j].name + '_day' + str(day) + '.csv') 
	queues_avg /= float(var.episodes)
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
	path = '/home/carolina/Documents/BogotaRL/br_marl/csv_files_train_t3/'
	figsize = (15, 10)
	cols = 2
	gs = gridspec.GridSpec(len(var.junctions[j].edges) // cols + 1, cols)
	gs.update(hspace=0.4)
	times_avg = pd.read_csv(path+'br_times_' + var.junctions[j].name + '_day' + str(0) + '.csv') 
	t = times_avg['currSod']
	for day in range(1,var.episodes):
		times_avg += pd.read_csv(path+'br_times_' + var.junctions[j].name + '_day' + str(day) + '.csv') 
	times_avg /= float(var.episodes)
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