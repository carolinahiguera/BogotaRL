import sys
import matplotlib
import numpy as np

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtCore import QThread, pyqtSignal

import pyqtgraph as pg

from comm_thread import CommThread
from my_mpl_canvas import MyMplCanvas
from var import *


matplotlib.use('TkAgg')

# TODO: Start time in GUI
# TODO: Legents for colors in travel times graphs
# TODO: Disable mouse interaction in plots
# TODO: Check buttons to disable methods
# TODO: Name of routes

class Mainwindow(QtWidgets.QMainWindow):

    update_speed = pyqtSignal(float)

    def __init__(self):
        super(Mainwindow, self).__init__(None)
        loadUi('gui_demo.ui', self)

        self.start_time = START_TIME
        self.time_interval = 0

        self.travel_times_buffer = []
        for i in range(NUM_ROUTES):
            self.travel_times_buffer.append([])
            for j in range(NUM_METHODS):
                self.travel_times_buffer[-1].append([
                    [],
                    np.empty(0),
                ])

        self.travel_times_figures = []
        self.travel_times_plots = []
        for route in range(NUM_ROUTES):
            self.travel_times_figures.append(pg.PlotWidget(title=f'Travel Times - Route {route + 1}'))
            self.travel_times_plots.append([])
            for method in range(NUM_METHODS):
                self.travel_times_plots[route].append(
                    self.travel_times_figures[route].plot(pen=pg.mkPen(COLOR_METHODS[method])))
            self.grid_tab_travels.addWidget(self.travel_times_figures[-1],
                                            route // NUM_TRAVEL_TIME_COLS,
                                            route % NUM_TRAVEL_TIME_COLS)

        self.green_waves_figures = []
        if GREEN_WAVES_FT:
            self.green_waves_figures.append(pg.PlotWidget(title=METHODS_NAMES[0]))
            self.grid_green_waves.addWidget(self.green_waves_figures[-1], 0, 0)
            plot1 = self.green_waves_figures[-1].plot(pen=pg.mkPen('r', width=20))
            plot2 = self.green_waves_figures[-1].plot(pen=pg.mkPen('g', width=20))
            plot1.setData([1, 2, 3, 4], [1, 1, 1, 1])
            plot2.setData([1, 2, 3, 4], [2, 2, 2, 2])

        for method in range(NUM_METHODS-1):
            self.green_waves_figures.append(pg.PlotWidget(title=METHODS_NAMES[method+1]))
            self.grid_green_waves.addWidget(self.green_waves_figures[-1],
                                            (method + 2) // NUM_GREEN_WAVES_COLS,
                                            (method+2) % NUM_GREEN_WAVES_COLS)




        self.set_plot_window(DEF_PLOT_WINDOW)
        self.radios_window = []
        for i, option in enumerate(PLOT_WINDOWS):
            self.radios_window.append(QRadioButton(option['label']))
            if i == DEF_PLOT_WINDOW:
                self.radios_window[-1].setChecked(True)
            self.radios_window[-1].clicked.connect(self.radio_window_clicked)
            self.window_size_layout.addWidget(self.radios_window[-1])

        self.radios_speed = []
        for i, option in enumerate(SIM_SPEEDS):
            self.radios_speed.append(QRadioButton(option['label']))
            if i == DEF_SIM_SPEED:
                self.radios_speed[-1].setChecked(True)
            self.radios_speed[-1].clicked.connect(self.radio_speed_clicked)
            self.sim_speed_layout.addWidget(self.radios_speed[-1])

        self.comm_thread_obj = CommThread()
        self.comm_thread_obj.send_log.connect(self.log, QtCore.Qt.BlockingQueuedConnection ) # QtCore.Qt.BlockingQueuedConnection
        self.comm_thread_obj.update_gui.connect(self.update_gui, QtCore.Qt.BlockingQueuedConnection )
        self.update_speed.connect(self.comm_thread_obj.update_speed)
        self.comm_thread_obj.start()

        self.update_speed.emit(SIM_SPEEDS[DEF_SIM_SPEED]['secs'])

    def radio_window_clicked(self):
        for i, radio in enumerate(self.radios_window):
            if radio.isChecked():
                self.set_plot_window(i)
                break

    def radio_speed_clicked(self):
        for i, radio in enumerate(self.radios_speed):
            if radio.isChecked():
                self.update_speed.emit(SIM_SPEEDS[i]['secs'])
                break

    def set_plot_window(self, option:int) -> None:
        ticks = [[]]
        for i in range(60 * 60 * 24):
            if i % (60 * PLOT_WINDOWS[option]['mins'] // 4) == 0:
                ticks[0].append((i, f'{i // (60 * 60):02}:{(i // 60) % 60:02}'))
        for route in range(NUM_ROUTES):
            xax = self.travel_times_figures[route].getAxis('bottom')
            xax.setTicks(ticks)
        self.time_interval = PLOT_WINDOWS[option]['mins'] * 60

    @pyqtSlot(int, dict)
    def update_gui(self, time:int, travel_times: dict) -> None:
        time = self.start_time*60*60+time
        if len(travel_times) > 0:
            for method in travel_times:
                for route in range(NUM_ROUTES):
                    # self.travel_times_buffer[route][method][0].append(timestamp())
                    self.travel_times_buffer[route][method][0] = \
                        np.append(self.travel_times_buffer[route][method][0],
                                  time)
                    self.travel_times_buffer[route][method][1] = \
                        np.append(self.travel_times_buffer[route][method][1],
                                  travel_times[method][route])

            for route in range(NUM_ROUTES):
                rmax = 0
                for method in range(NUM_METHODS):
                    self.travel_times_plots[route][method].setData( self.travel_times_buffer[route][method][0],
                                                                    self.travel_times_buffer[route][method][1])
                    # print(self.travel_times_buffer[route][method][0])
                    if self.travel_times_buffer[route][method][0] != []:
                        mmax = np.max(self.travel_times_buffer[route][method][1][self.travel_times_buffer[route][method][0]>(time - self.time_interval)])
                        if mmax>rmax:
                            rmax = mmax
                self.travel_times_figures[route].setXRange(time - self.time_interval, time)
                self.travel_times_figures[route].setYRange(0, rmax)

    @pyqtSlot(str)
    def log(self, text:str) -> None:
        self.text_log.append(text)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = Mainwindow()
    ui.setWindowTitle('Test')
    ui.show()
    sys.exit(app.exec_())
