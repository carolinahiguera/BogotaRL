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

file_path = "/media/camilo/UUI/minicityTF"

travels = None
travels_flag = False

def moving_average(a, n=AVG_SIZE) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

for agent in routes[0]['route_agents']:
    queues = np.genfromtxt(
        f'/media/camilo/UUI/minicityTF/dfQueue_testTF_int{agent}_day0.csv',
        delimiter=',')[1:,2+routes[0]['route_edges_i'][agent]]
    # queues = moving_average(queues)
    speeds = np.genfromtxt(
        f'/media/camilo/UUI/minicityTF/dfSpeed_testTF_int{agent}_day0.csv',
        delimiter=',')[1:,2+routes[0]['route_edges_i'][agent]]
    # speeds = moving_average(speeds)
    speeds[queues==0] = 0.0
    queues[queues==0] = 1.0
    speeds = speeds/queues
    waiting = np.genfromtxt(
        f'/media/camilo/UUI/minicityTF/dfWaiting_testTF_int{agent}_day0.csv',
        delimiter=',')[1:,2+routes[0]['route_edges_i'][agent]]
    # waiting = moving_average(waiting)

    lens = np.ones(len(waiting)) * routes[0]['route_edges_len'][agent]
    lens[speeds<1.0] = 0.0
    speeds[speeds<1.0] = 1.0
    travel_times = waiting + lens / speeds
    travel_times /= 60.0

    if not travels_flag:
        travels_flag = True
        travels = np.empty([0, len(travel_times)])

    travels = np.append(travels, [travel_times], axis=0)

travels = np.sum(travels, axis=0)
plt.plot(travels, 'b')

######

travels = None
travels_flag = False

for agent in routes[0]['route_agents']:
    queues = np.genfromtxt(
        f'/media/camilo/UUI/indQ/dfQueue_test_agt{agent}_day0.csv',
        delimiter=',')[1:,2+routes[0]['route_edges_i'][agent]]
    # queues = moving_average(queues)
    speeds = np.genfromtxt(
        f'/media/camilo/UUI/indQ/dfMeanSpeed_test_agt{agent}_day0.csv',
        delimiter=',')[1:,2+routes[0]['route_edges_i'][agent]]
    # speeds = moving_average(speeds)
    speeds[queues==0] = 0.0
    queues[queues==0] = 1.0
    speeds = speeds/queues
    waiting = np.genfromtxt(
        f'/media/camilo/UUI/indQ/dfWaiting_test_agt{agent}_day0.csv',
        delimiter=',')[1:,2+routes[0]['route_edges_i'][agent]]
    # waiting = moving_average(waiting)

    lens = np.ones(len(waiting)) * routes[0]['route_edges_len'][agent]
    lens[speeds<1.0] = 0.0
    speeds[speeds<1.0] = 1.0
    travel_times = waiting + lens / speeds
    travel_times /= 60.0

    if not travels_flag:
        travels_flag = True
        travels = np.empty([0, len(travel_times)])

    travels = np.append(travels, [travel_times], axis=0)

travels = np.sum(travels, axis=0)
plt.plot(travels, 'r')

plt.show()