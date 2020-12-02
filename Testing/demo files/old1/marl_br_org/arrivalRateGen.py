'''
Created on 21/09/2016

@author: carolina
'''
from random import randint
import pandas as pd
import numpy as np
import random
import var

#Parameters and variables
arrivalScaling = 0.475
maxTypeVeh = 8
colNames = []
functions = []

def createPolyFlow():
    global colNames, functions
    
    xls = pd.ExcelFile(var.project+'.xlsx')
    dfArrivalData = xls.parse('rutas')
    aux = ['hour']
    for i in range(0,len(var.routesList)):
        aux.append(str(i))
    dfArrivalData.columns = aux
    colNames = list(dfArrivalData.columns.values)
    x = dfArrivalData['hour']
    
    for j in range(0,len(colNames)-1):        
        newCol = str(colNames[j+1])        
        y = dfArrivalData[newCol]        
        p = np.polyfit(x, y, 12)        
        functions.append(np.poly1d(p))


def writeRoutes(seed):
    #import random
    arrivals = []
    random.seed(seed)
    for z in range(len(functions)):
        sod = 0.0
        while sod < var.secondsInDay:
            hod = sod/(60*60.0)
            arrivalRate = max(1,functions[z](hod)*arrivalScaling)
            iaTimeSeconds = random.expovariate(arrivalRate)*60.0
            typeVeh = randint(0,maxTypeVeh)   
            arrivals.append([sod, colNames[z+1], typeVeh])
            sod += iaTimeSeconds

    arrivals.sort()

    
    # Open the file
    with open(var.project+'.rou.xml', 'w') as routes:
        routes.write("""<?xml version="1.0"?>""" + '\n' + '\n')
        routes.write("""<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">""" + '\n')
        routes.write('\n')
        routes.write("""<vType accel="3.0" decel="6.0" id="Car0" length="4.0"  minGap="2.0" maxSpeed="50.0" sigma="0.5" color="1,0,0" guiShape="passenger" probability="0.356"/>""" + '\n')
        routes.write("""<vType accel="3.0" decel="6.0" id="Car1" length="5.0"  minGap="1.5" maxSpeed="50.0" sigma="0.5" color="0,1,0" guiShape="passenger/sedan" probability="0.356"/>""" + '\n')
        routes.write("""<vType accel="3.0" decel="6.0" id="Car2" length="6.0"  minGap="1.0" maxSpeed="45.0" sigma="0.5" color="0,0,1" guiShape="passenger/hatchback" probability="0.178"/>""" + '\n')
        routes.write("""<vType accel="2.0" decel="6.0" id="Car3" length="7.0"  minGap="2.5" maxSpeed="50.0" sigma="0.5" color="1,1,0" guiShape="passenger/van" probability="0.036"/>""" + '\n')
        routes.write("""<vType accel="3.0" decel="6.0" id="Car4" length="8.0"  minGap="2.0" maxSpeed="45.0" sigma="0.5" color="1,0,1" guiShape="passenger/van" probability="0.045"/>""" + '\n')
        routes.write("""<vType accel="2.0" decel="5.0" id="Car5" length="9.0"  minGap="1.5" maxSpeed="45.0" sigma="0.5" color="0,1,1" guiShape="bus" probability="0.009"/>""" + '\n')
        routes.write("""<vType accel="2.0" decel="5.0" id="Car6" length="10.0" minGap="1.5" maxSpeed="45.0" sigma="0.5" color="1,1,1" guiShape="bus" probability="0.010"/>""" + '\n')
        routes.write("""<vType accel="1.5" decel="5.0" id="Car7" length="11.0" minGap="2.0" maxSpeed="40.0" sigma="0.5" color="0.5,0.5,0.5" guiShape="truck" probability="0.006"/>""" + '\n')
        routes.write("""<vType accel="1.0" decel="5.0" id="Car8" length="12.0" minGap="2.5" maxSpeed="35.0" sigma="0.5" color="0.8,0.8,0.8" guiShape="truck" probability="0.004"/>""" + '\n')
        routes.write('\n')    
        for i in range(len(var.routesList)):
            routes.write("""<route id=\"""" + str(i) + """\"""" + """ edges=\"""" + var.routesList[i] + """\"/> """ + '\n')
            
        routes.write('\n')
        idCounter = 0
        for i in arrivals:
            vType = """\" type=\"Car""" + str(i[2])
            routes.write("""<vehicle id=\"""" + str(idCounter) + """\" depart=\"""" + str(round(i[0],2)) + """\" route=\"""" + str(i[1]) + vType + """\"/>""" + '\n')
            idCounter += 1
        routes.write("""</routes>""")