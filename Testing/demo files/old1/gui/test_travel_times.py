import numpy as np
from numpy import genfromtxt
import os
import matplotlib.pyplot as plt

AVG_SIZE = 50

routes = {}
routes[0] = {}
routes[0]['route_agents'] = [5,4,3]
routes[0]['route_edge'] = ['A5N', 'A4N', 'A3N']#[2,2,1]
routes[0]['route_edges_i'] = {5:0,4:0,3:0}
routes[0]['route_edges_len'] = {5:114.56, 4:116.97, 3:129.71}
routes[0]['name'] = 'Route 1: Ak7 North-South'

print('hola')

MAX_TIME = 70000

####

file_path = "../FT/trackers"

time = 0

plot_x = np.zeros(MAX_TIME//24+1)
plot_y = np.zeros(MAX_TIME//24+1)

while time<=MAX_TIME: #84600
    print(f'FT:{(100*time)//MAX_TIME}%')
    travel_time = 0.0
    for agent in routes[0]['route_agents']:
        file = f'{file_path}/dfSpeedTracker{agent}_{time}.csv'
        x = np.genfromtxt(file, delimiter=',')
        speed = np.mean(x[1:, 1:], axis=0)[routes[0]['route_edges_i'][agent]]
        file = f'{file_path}/dfWaitingTracker{agent}_{time}.csv'
        x = np.genfromtxt(file, delimiter=',')
        waiting = np.mean(x[1:, 1:], axis=0)[routes[0]['route_edges_i'][agent]]
        file = f'{file_path}/dfQueueTracker_agt{agent}_{time}.csv'
        x = np.genfromtxt(file, delimiter=',')
        queue = np.mean(x[1:, 1:], axis=0)[routes[0]['route_edges_i'][agent]]
        waiting = waiting / queue if queue!=0 else 0.0
        # print(f'speed:{speed}')
        # print(f'waiting:{waiting}')
        if speed >= 1.0:
            travel_time += waiting + routes[0]['route_edges_len'][agent]/speed
        else:
            travel_time += waiting
    travel_time /= 60
    plot_x[time // 24] = time
    plot_y[time // 24] = travel_time
    time += 24

plt.plot(plot_x, plot_y, 'b')

#####

file_path = "../indQ/trackers"

time = 0

plot_x = np.zeros(MAX_TIME//24+1)
plot_y = np.zeros(MAX_TIME//24+1)

while time<=MAX_TIME:
    print(f'indQ:{(100*time)//MAX_TIME}%')
    travel_time = 0.0
    for agent in routes[0]['route_agents']:
        file = f'{file_path}/dfSpeedTracker{agent}_{time}.csv'
        x = np.genfromtxt(file, delimiter=',')
        speed = np.mean(x[1:, 1:], axis=0)[routes[0]['route_edges_i'][agent]]
        file = f'{file_path}/dfWaitingTracker{agent}_{time}.csv'
        x = np.genfromtxt(file, delimiter=',')
        waiting = np.mean(x[1:, 1:], axis=0)[routes[0]['route_edges_i'][agent]]
        file = f'{file_path}/dfQueueTracker_agt{agent}_{time}.csv'
        x = np.genfromtxt(file, delimiter=',')
        queue = np.mean(x[1:, 1:], axis=0)[routes[0]['route_edges_i'][agent]]
        waiting = waiting / queue if queue!=0 else 0.0
        # print(f'speed:{speed}')
        # print(f'waiting:{waiting}')
        if speed >= 1.0:
            travel_time += waiting + routes[0]['route_edges_len'][agent]/speed
        else:
            travel_time += waiting
    travel_time /= 60
    plot_x[time // 24] = time
    plot_y[time // 24] = travel_time
    time += 24

plt.plot(plot_x, plot_y, 'r')
plt.show()

# while i<=2616:
