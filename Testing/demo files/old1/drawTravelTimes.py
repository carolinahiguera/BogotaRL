import numpy as np
import matplotlib
import random

matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import traci
sumoBinary = "sumo-gui" #sumo-gui
sumoCmd = [sumoBinary, "-c", "./miniCity/miniCity.sumo.cfg", "--no-step-log", "true"]

from FT.agentTF import agentTF
from var import *


class MyMplCanvas(FigureCanvas): 
    def __init__(self, parent=None, width=5, height=4, dpi=100, route=1):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.route = route
        self.hl, = self.axes.plot([], [])

    def compute_initial_figure(self):
        pass


class MplTravelTime(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.load_agents()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)
        #traci.start(sumoCmd, label="sim"+str(self.route))
        self.counter = -1

    def compute_initial_figure(self):
        self.hl, = self.axes.plot([], [], 'r')

    def update_figure(self, sec, new_data):
        self.hl.set_xdata(np.append(self.hl.get_xdata(), self.counter))
        self.hl.set_ydata(np.append(self.hl.get_ydata(), new_data))
        self.axes.plot(self.hl.get_xdata(), self.hl.get_ydata(), 'r')
        self.draw()
        traci.switch("sim"+str(self.route))
        traci.simulationStep()

    def load_agents(self):
        #FT
        agentsTF = {}
        for i in range(6):
            agentsTF[i] = agentTF(junctions['ID'][i],                                  
                                  junctions['listLanes'][i],
                                  junctions['listEdges'][i],
                                  junctions['numberLanes'][i],
                                  junctions['actionPhases'][i],
                                  junctions['auxPhases'][i],                                
                                  junctions['planProgram'][i],
                                  junctions['neigbors'][i])



