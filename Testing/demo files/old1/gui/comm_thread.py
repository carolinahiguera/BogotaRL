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
    update_gui = pyqtSignal(int, dict)

    def __init__(self):
        self.time_sleep = 0.0
        self.mutex = Lock()
        self.agents_state = np.array(INITIAL_AGENTS_STATE)
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

        while True:

            time = None
            travel_times = {}

            for i, pipe in enumerate(PIPES_NAMES):
                self.mutex.acquire()
                sleep(self.time_sleep)
                self.mutex.release()
                fifo = open(pipe, 'wb')
                fifo.write('step'.encode('utf-8'))
                fifo.close()
                fifo = open(pipe, 'rb')
                data.ParseFromString(fifo.read())
                time = data.time_stamp
                fifo.close()
                if len(data.travel_times)>0:
                    times = np.array(data.travel_times)
                    if not np.isnan(times).any():
                        travel_times[i] = np.array(data.travel_times)

            # if len(travel_times)>0:
            #     self.update_gui.emit(time, travel_times)

            print(travel_times)
            # print(data)
            # for agent in data.action:
            #     if agent.

            self.update_gui.emit(time, travel_times)
