import os, sys


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    print(tools)
    sys.path.append(tools)
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")

from drawTravelTimes import *



class mainwindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mainwindow,self).__init__(None)
        loadUi('gui_marl.ui',self)

        r1 = MplTravelTime(self.widget_times, width=5, height=4, dpi=100, route=1)
        r2 = MplTravelTime(self.widget_times, width=5, height=4, dpi=100, route=2)
        #r3 = MplTravelTime(self.widget_times, width=5, height=4, dpi=100, route=3)
        #r4 = MplTravelTime(self.widget_times, width=5, height=4, dpi=100, route=4)
        self.layoutTimes1.addWidget(r1)
        self.layoutTimes1.addWidget(r2)
        #self.layoutTimes2.addWidget(r3)
        #self.layoutTimes2.addWidget(r4)
        self.widget_times.setFocus()
      

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = mainwindow()
    ui.setWindowTitle('MARL for traffic control')
    ui.show()   
    sys.exit(app.exec_())