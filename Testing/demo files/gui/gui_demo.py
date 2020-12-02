import sys
import numpy as np
from copy import deepcopy
import stat, os

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore, QtSvg
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QRadioButton
# from PyQt5.QtCore import QThread, pyqtSignal

import pyqtgraph as pg

from sumo_data_pb2 import SumoData

# from comm_thread import CommThread
from var import *

class Mainwindow(QtWidgets.QMainWindow):

    # update_speed = pyqtSignal(float)

    def __init__(self):
        super(Mainwindow, self).__init__(None)
        loadUi('gui_demo.ui', self)
        self.showFullScreen()
        self.btnExit.clicked.connect(self.clickExit)
        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.tabChanged(self.tabWidget.currentIndex())

        svgCurves= QtSvg.QSvgWidget('img/curves.svg')
        self.layoutCurves.addWidget(svgCurves)
        svgMap= QtSvg.QSvgWidget('img/map.svg')
        self.layoutMap.addWidget(svgMap)
        svgLegends = QtSvg.QSvgWidget('img/legends.svg')
        self.layoutLegends.addWidget(svgLegends)

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
            # self.travel_times_figures.append(pg.PlotWidget(title=f'Travel Times - Route {route + 1}'))
            self.travel_times_figures.append(pg.PlotWidget())
            self.travel_times_figures[-1].setMouseEnabled(False, False)
            titleStyle = {'color': '#969696', 'size': '18pt'}
            self.travel_times_figures[-1].setTitle(f'Route {route + 1}: {ROUTES_NAMES[route]}', **titleStyle)
            self.travel_times_figures[-1].setLabel('bottom', '<font size="4">Time</font>')
            self.travel_times_figures[-1].setLabel('left', '<font size="4">Travel times (min)</font>')
            self.travel_times_plots.append([])
            for method in range(NUM_METHODS):
                self.travel_times_plots[route].append(
                    self.travel_times_figures[route].plot(pen=pg.mkPen(COLOR_METHODS[method])))
            self.grid_tab_travels.addWidget(self.travel_times_figures[-1],
                                            route // NUM_TRAVEL_TIME_COLS,
                                            route % NUM_TRAVEL_TIME_COLS)


        self.green_waves_plots = dict((el, dict((el2, None) for el2 in TEST_ROUTE['route_agents'])) for el in PIPES_NAMES)
        # self.green_routes_plots = dict((el, None) for el in PIPES_NAMES)
        self.green_routes_flags = dict((el, 0) for el in PIPES_NAMES)
        self.green_routes_data = dict((el, np.empty([2,0])) for el in PIPES_NAMES)
        self.green_waves_buffer = dict((el, dict((el2, np.empty([2,0])) for el2 in TEST_ROUTE['route_agents'])) for el in PIPES_NAMES)
        self.prev_phases = dict((el, dict((el2, -1) for el2 in TEST_ROUTE['route_agents'])) for el in PIPES_NAMES)
        self.next_time = dict((el, None) for el in PIPES_NAMES)
        self.next_time = dict((el, None) for el in PIPES_NAMES)
        self.green_routes_plots = dict((el, np.empty([2, 2])) for el in PIPES_NAMES)
        self.green_routes_ok = dict((el, True) for el in PIPES_NAMES)

        self.green_waves_figures = {}
        self.green_waves_figures[PIPES_NAMES[0]] = pg.PlotWidget()
        self.green_waves_figures[PIPES_NAMES[0]].setMouseEnabled(False, False)

        if GREEN_WAVES_FT:
            self.grid_green_waves.addWidget( self.green_waves_figures[PIPES_NAMES[0]] , 0, 0)
            svgMap = QtSvg.QSvgWidget('img/map2.svg')
            self.grid_green_waves.addWidget(svgMap, 0, 1)
            titleStyle = {'color': '#969696', 'size': '18pt'}
            self.green_waves_figures[PIPES_NAMES[0]].setTitle(METHODS_NAMES[0], **titleStyle)
            self.green_waves_figures[PIPES_NAMES[0]].setLabel('bottom', '<font size="4">Time</font>')
            self.green_waves_figures[PIPES_NAMES[0]].setLabel('left', '<font size="4">Agent</font>')
            xax = self.green_waves_figures[PIPES_NAMES[0]].getAxis('left')
            xax.setTicks(TEST_ROUTE['agent_labels'])


        for method in range(NUM_METHODS - 1):
            self.green_waves_figures[PIPES_NAMES[method + 1]] = pg.PlotWidget(title=METHODS_NAMES[method + 1])
            self.green_waves_figures[PIPES_NAMES[method + 1]].setMouseEnabled(False, False)
            titleStyle = {'color': '#969696', 'size': '18pt'}
            self.green_waves_figures[PIPES_NAMES[method + 1]].setTitle(METHODS_NAMES[method + 1], **titleStyle)
            self.green_waves_figures[PIPES_NAMES[method + 1]].setLabel('bottom', '<font size="4">Time</font>')
            self.green_waves_figures[PIPES_NAMES[method + 1]].setLabel('left', '<font size="4">Agent</font>')
            xax = self.green_waves_figures[PIPES_NAMES[method + 1]].getAxis('left')
            xax.setTicks(TEST_ROUTE['agent_labels'])
            self.grid_green_waves.addWidget(self.green_waves_figures[PIPES_NAMES[method + 1]],
                                            (method + 2) // NUM_GREEN_WAVES_COLS,
                                            (method + 2) % NUM_GREEN_WAVES_COLS)

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

        # self.comm_thread_obj = CommThread()
        # self.comm_thread_obj.send_log.connect(self.log, QtCore.Qt.BlockingQueuedConnection )
        # self.comm_thread_obj.update_gui.connect(self.update_gui, QtCore.Qt.BlockingQueuedConnection )
        # self.update_speed.connect(self.comm_thread_obj.update_speed)
        # self.comm_thread_obj.start()
        # self.update_speed.emit(SIM_SPEEDS[DEF_SIM_SPEED]['secs'])

        for pipe_name in PIPES_NAMES:
            try:
                if stat.S_ISFIFO(os.stat(pipe_name).st_mode):
                    os.remove(pipe_name)
                else:
                    os.remove(pipe_name)
            except:
                pass
            os.mkfifo(pipe_name)

        self.avg_speeds = dict((el, dict((el2, 1.0) for el2 in TEST_ROUTE['route_agents'])) for el in PIPES_NAMES)

        self.comm_timer = QTimer()
        self.comm_timer.timeout.connect(self.conn_timer_tick)
        self.comm_timer.start(SIM_SPEEDS[DEF_SIM_SPEED]['secs'])


    def tabChanged(self, x):
        if x==0:
            self.groupLegends.show()
            self.groupWindowSize.show()
            self.groupSimSpeed.show()
            self.btnExit.show()
        elif x==1:
            self.groupLegends.hide()
            self.groupWindowSize.show()
            self.groupSimSpeed.show()
            self.btnExit.show()
        elif x == 2:
            self.groupLegends.hide()
            self.groupWindowSize.hide()
            self.groupSimSpeed.hide()
            self.btnExit.hide()
        elif x == 3:
            self.groupLegends.hide()
            self.groupWindowSize.hide()
            self.groupSimSpeed.hide()
            self.btnExit.hide()

    def clickExit(self):
        QtCore.QCoreApplication.instance().quit()

    def conn_timer_tick(self):
        data = SumoData()
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
            if len(data.travel_times) > 0:
                times = np.array(data.travel_times)
                if not np.isnan(times).any():
                    travel_times[i] = np.array(data.travel_times)
            if len(data.action) > 0:
                phases[pipe] = {}
                for act in data.action:
                    if act.agent_id in TEST_ROUTE['route_agents']:
                        if act.action == GREEN_PHASE[pipe][act.agent_id]:
                            phases[pipe][act.agent_id] = 1
                        else:
                            phases[pipe][act.agent_id] = 0
            if len(data.mean_speed) > 0:
                for speed in data.mean_speed:
                    if speed.agent_id in TEST_ROUTE['route_agents']:
                        avg_speed = speed.speed[TEST_ROUTE['route_edges_i'][speed.agent_id]]
                        if avg_speed >= 1.0:
                            self.avg_speeds[pipe][speed.agent_id] = avg_speed

        print(self.avg_speeds)

        self.update_gui(time, travel_times, phases, self.avg_speeds)

    def radio_window_clicked(self):
        for i, radio in enumerate(self.radios_window):
            if radio.isChecked():
                self.set_plot_window(i)
                break

    def radio_speed_clicked(self):
        for i, radio in enumerate(self.radios_speed):
            if radio.isChecked():
                self.comm_timer.setInterval(SIM_SPEEDS[i]['secs'])
                break

    def set_plot_window(self, option:int) -> None:
        ticks = [[]]
        for i in range(60 * 60 * 24):
            if i % (60 * PLOT_WINDOWS[option]['mins'] // 4) == 0:
                ticks[0].append((i, f'{i // (60 * 60):02}:{(i // 60) % 60:02}'))
        for route in range(NUM_ROUTES):
            xax = self.travel_times_figures[route].getAxis('bottom')
            xax.setTicks(ticks)
        for method in PIPES_NAMES:
            xax = self.green_waves_figures[method].getAxis('bottom')
            xax.setTicks(ticks)
        self.time_interval = PLOT_WINDOWS[option]['mins'] * 60

    # @pyqtSlot(int, dict, dict, dict)
    def update_gui(self, time:int, travel_times: dict, phases: dict, avg_speeds: dict) -> None:

        # start = time_lib.time()

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

        if len(phases):
            for method in phases:
                for agent in phases[method]:
                    if phases[method][agent] != self.prev_phases[method][agent]:
                        self.green_waves_buffer[method][agent] = np.empty([2,0])
                        if phases[method][agent]==0:
                            self.green_waves_plots[method][agent] = self.green_waves_figures[method].plot(pen=pg.mkPen('r', width=WIDTH_PHASES))
                        else:
                            self.green_waves_plots[method][agent] = self.green_waves_figures[method].plot(pen=pg.mkPen('g', width=WIDTH_PHASES))
                    self.green_waves_buffer[method][agent] = np.append(self.green_waves_buffer[method][agent], [[time],[TEST_ROUTE['plot_order'][agent]]], axis=1)
                    self.green_waves_plots[method][agent].setData(self.green_waves_buffer[method][agent][0],
                                                                      self.green_waves_buffer[method][agent][1])
                self.green_waves_figures[method].setXRange(time - self.time_interval, time-(self.time_interval/20))

                # print(self.green_routes_flags[method])

                if self.green_routes_flags[method] == 0:
                    self.green_routes_plots[method] = np.empty([2, 2])
                    self.green_routes_ok[method] = True
                    if phases[method][TEST_ROUTE['route_agents'][0]] == 1:
                        n_time = time + TEST_ROUTE['distances'][0] / avg_speeds[method][4]
                        self.green_routes_plots[method][0] = [time, n_time]
                        self.green_routes_flags[method] = 1
                elif self.green_routes_flags[method] == 1:
                    if time >= self.green_routes_plots[method][0][1]:
                        if phases[method][TEST_ROUTE['route_agents'][1]] == 1:
                            n_time = time + TEST_ROUTE['distances'][1] / avg_speeds[method][3]
                            self.green_routes_plots[method][1] = [time, n_time]
                            self.green_routes_flags[method] = 3
                        else:
                            self.green_routes_ok[method] = False
                            self.green_routes_flags[method] = 2
                elif self.green_routes_flags[method] == 2:
                    if phases[method][TEST_ROUTE['route_agents'][1]] == 1:
                        n_time = time + TEST_ROUTE['distances'][1] / avg_speeds[method][3]
                        self.green_routes_plots[method][1] = [time, n_time]
                        self.green_routes_flags[method] = 3
                elif self.green_routes_flags[method] == 3:
                    if time >= self.green_routes_plots[method][1][1]:
                        if phases[method][TEST_ROUTE['route_agents'][2]] == 0:
                            self.green_routes_ok[method] = False
                        color = 'g' if self.green_routes_ok[method] else 'w'
                        temp_plot = self.green_waves_figures[method].plot(
                            pen=pg.mkPen(color, width=WIDTH_ROUTE, style=QtCore.Qt.DashLine))
                        temp_plot.setData(self.green_routes_plots[method][0], [1, 2])
                        temp_plot = self.green_waves_figures[method].plot(
                            pen=pg.mkPen(color, width=WIDTH_ROUTE, style=QtCore.Qt.DashLine))
                        temp_plot.setData(self.green_routes_plots[method][1], [2, 3])
                        self.green_routes_flags[method] = 4
                elif self.green_routes_flags[method] == 4:
                    if phases[method][TEST_ROUTE['route_agents'][1]] == 0:
                        self.green_routes_flags[method] = 0

            self.prev_phases = deepcopy(phases)

        # end = time_lib.time()
        # print(end - start)

    @pyqtSlot(str)
    def log(self, text:str) -> None:
        self.text_log.append(text)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = Mainwindow()
    ui.setWindowTitle('Test')
    ui.show()
    sys.exit(app.exec_())
