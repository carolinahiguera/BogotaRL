from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import pyqtSlot

from threading import Lock
from time import sleep
import random
import stat, os
import numpy as np
from var import *

from sumo_data_pb2 import SumoData

class CommThread(QThread):

    send_log = pyqtSignal(str)
    update_gui = pyqtSignal(int, dict, dict, dict)

    def __init__(self):
        self.time_sleep = 0.0
        self.mutex = Lock()
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def init_pipes(self):
        for pipe_name in PIPES_NAMES:
            try:
                if stat.S_ISFIFO(os.stat(pipe_name).st_mode):
                    os.remove(pipe_name)
                else:
                    os.remove(pipe_name)
            except:
                pass
            os.mkfifo(pipe_name)

    @pyqtSlot(float)
    def update_speed(self, time:float) -> None:
        self.mutex.acquire()
        self.time_sleep = time
        self.mutex.release()

    def log(self, text):
        self.send_log.emit(f'[ct]: {text}')

    def run(self):
        self.init_pipes()
        data = SumoData()

        for pipe in PIPES_NAMES:
            self.log(f'Waiting pipe: {pipe}')
            fifo = open(pipe, 'wb')
            fifo.write('step'.encode('utf-8'))
            fifo.close()
            fifo = open(pipe, 'rb')
            data.ParseFromString(fifo.read())
            fifo.close()
            self.log(f'Connected to pipe: {pipe}')

        avg_speeds = dict((el, dict((el2, 1.0) for el2 in TEST_ROUTE['route_agents'])) for el in PIPES_NAMES)

        while True:

            self.mutex.acquire()
            sleep(self.time_sleep)
            self.mutex.release()

            time = None
            travel_times = {}
            phases = {}

            for i, pipe in enumerate(PIPES_NAMES):
                fifo = open(pipe, 'wb')
                fifo.write('step'.encode('utf-8'))
                fifo.close()

            for i, pipe in enumerate(PIPES_NAMES):
                fifo = open(pipe, 'rb')
                data.ParseFromString(fifo.read())
                time = data.time_stamp
                fifo.close()
                if len(data.travel_times)>0:
                    times = np.array(data.travel_times)
                    if not np.isnan(times).any():
                        travel_times[i] = np.array(data.travel_times)
                if len(data.action)>0:
                    phases[pipe] = {}
                    for act in data.action:
                        if act.agent_id in TEST_ROUTE['route_agents']:
                            if act.action == GREEN_PHASE[pipe][act.agent_id]:
                                phases[pipe][act.agent_id] = 1
                            else:
                                phases[pipe][act.agent_id] = 0
                if len(data.mean_speed)>0:
                    for speed in data.mean_speed:
                        if speed.agent_id in TEST_ROUTE['route_agents']:
                            avg_speed = speed.speed[ TEST_ROUTE['route_edges_i'][speed.agent_id] ]
                            if avg_speed>=1.0:
                                avg_speeds[pipe][speed.agent_id] = avg_speed

            self.update_gui.emit(time, travel_times, phases, avg_speeds)
