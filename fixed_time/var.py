'''
Created on Nov 21, 2017

@author: carolina
'''
import junction
exec(open("./junction.py").read())
#execfile("./junction.py")
import TLS
exec(open("./TLS.py").read())
#execfile("./TLS.py")

global port, secondsInDay, episodes, sampleTime
#avilable_ports = [8813, 8814, 8815, 8816, 8817, 8818, 8819, 8820] 
#port = avilable_ports[2]

secondsInDay = 46800#46800
episodes = 5
sampleTime = 1
timeYellow = 3
beta = [0.5, 2.0]
theta = [1.75, 3.0]
exp = [2.0, 1.5]

#====================== Juntion properties ======================
junctions = {}

name = 'AK13CL45'
ID = 0
edges = ['89704070#4', '24324743#2', 'gneE46']
lanes = [['89704070#4_0', '89704070#4_1', '89704070#4_2'], 
         ['24324743#2_0', '24324743#2_1'],
         ['gneE46_0', 'gneE46_1']]
lenght_lanes = [[87.40, 87.40, 87.40],[163.76, 163.76],[115.44, 115.44]]
tls = 'tls_13_45'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK13CL46'
ID = 1
edges = ['89704070#3', '89704000#0', '-89704106']
lanes = [['89704070#3_0', '89704070#3_1', '89704070#3_2'], 
         ['89704000#0_0', '89704000#0_1'],
         ['-89704106_0']]
lenght_lanes = [[108.93, 108.93, 108.93],[71.25, 71.25],[118.08]]
tls = 'tls_13_46_47'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK13CL47'
ID = 2
edges = ['89704070#2', '38495054#2']
lanes = [['89704070#2_0', '89704070#2_1', '89704070#2_2'], 
         ['38495054#2_0', '38495054#2_1', '38495054#2_2']]
lenght_lanes = [[102.53, 102.53, 102.53],[80.67, 80.67, 80.67]]
tls = 'tls_13_46_47'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK13CL49'
ID = 3
edges = ['89704070#0', '-89702293#4']
lanes = [['89704070#0_0', '89704070#0_1', '89704070#0_2'], 
         ['-89702293#4_0', '-89702293#4_1']]
lenght_lanes = [[94.74, 94.74, 94.74],[109.48, 109.48]]
tls = 'tls_13_49_50'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK13CL50'
ID = 4
edges = ['89702308#0', '24322998']
lanes = [['89702308#0_0', '89702308#0_1', '89702308#0_2'], 
         ['24322998_0', '24322998_1']]
lenght_lanes = [[100.46, 100.46, 100.46],[113.67, 113.67]]
tls = 'tls_13_49_50'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK13CL51'
ID = 5
edges = ['89702306', '-89702448#1']
lanes = [['89702306_0', '89702306_1', '89702306_2'], 
         ['-89702448#1_0', '-89702448#1_1']]
lenght_lanes = [[97.55, 97.55, 97.55],[127.30, 127.30]]
tls = 'tls_13_51'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK13CL53'
ID = 6
edges = ['89700459#1', '352421883#1', 'gneE31']
lanes = [['89700459#1_0', '89700459#1_1', '89700459#1_2'], 
         ['352421883#1_0', '352421883#1_1'],
         ['gneE31_0', 'gneE31_1']]
lenght_lanes = [[115.22, 115.22, 115.22],[91.52, 91.52],[111.90, 111.90]]
tls = 'tls_13_53'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK14CL45'
ID = 7
edges = ['89704086#2.0', '79378213.0', '89704116#1.0', '200231874#2.0']
lanes = [['89704086#2.0_0', '89704086#2.0_1'], 
         ['79378213.0_0', '79378213.0_1'],
         ['89704116#1.0_0', '89704116#1.0_1'],
         ['200231874#2.0_0', '200231874#2.0_1']]
lenght_lanes = [[37.40,37.40],[119.94,119.94],[85.60,85.60],[99.00,99.00]]
tls = 'tls_14_45'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK14CL47'
ID = 8
edges = ['89702397.0', '89702498', '89702344#2.0']
lanes = [['89702397.0_0', '89702397.0_1'], 
         ['89702498_0', '89702498_1'],
         ['89702344#2.0_0', '89702344#2.0_1']]
lenght_lanes = [[100.10,100.10],[115.83,115.83],[113.65,113.65]]
tls = 'tls_14_47'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK14CL49'
ID = 9
edges = ['89702450#0.0', '-89702293#3.0', '89702344#4.0']
lanes = [['89702450#0.0_0', '89702450#0.0_1'], 
         ['-89702293#3.0_0', '-89702293#3.0_1'],
         ['89702344#4.0_0', '89702344#4.0_1']]
lenght_lanes = [[98.32,98.32],[116.31,116.31],[105.42,105.42]]
tls = 'tls_14_49'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK14CL51'
ID = 10
edges = ['24322994', '89702344#7', '89702405#0']
lanes = [['24322994_0', '24322994_1'], 
         ['89702344#7_0', '89702344#7_1'],
         ['89702405#0_0', '89702405#0_1']]
lenght_lanes = [[112.37,112.37],[98.98,98.98],[100.78,100.78]]
tls = 'tls_14_51'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK14CL53'
ID = 11
edges = ['89700369', '89700398.0', '89702344#10.0', '89759664#1.0']
lanes = [['89700369_0', '89700369_1'], 
         ['89700398.0_0', '89700398.0_1'],
         ['89702344#10.0_0', '89702344#10.0_1'],
         ['89759664#1.0_0', '89759664#1.0_1']]
lenght_lanes = [[119.07,119.07],[111.78,111.78],[96.22,96.22],[94.99,94.99]]
tls = 'tls_14_53'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK7CL45'
ID = 12
edges = ['89703989#0', '89717070#0', '313257098#0']
lanes = [['89703989#0_0', '89703989#0_1', '89703989#0_2'], 
         ['89717070#0_0', '89717070#0_1', '89717070#0_2'],
         ['313257098#0_0', '313257098#0_1']]
lenght_lanes = [[121.77, 121.77, 121.77],[126.73, 126.73, 126.73],[240.03, 240.03]]
tls = 'tls_7_45'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK7CL46'
ID = 13
edges = ['89702377', '89704091#2', '89704047#0']
lanes = [['89702377_0', '89702377_1', '89702377_2'], 
         ['89704091#2_0', '89704091#2_1'],
         ['89704047#0_0', '89704047#0_1', '89704047#0_2']]
lenght_lanes = [[107.90,107.90,107.90],[72.11,72.11],[121.65,121.65,121.65]]
tls = 'tls_7_46'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK7CL47'
ID = 14
edges = ['89702288#3', '381866506#0', '89702287#0']
lanes = [['89702288#3_0', '89702288#3_1', '89702288#3_2'], 
         ['381866506#0_0', '381866506#0_1'],
         ['89702287#0_0', '89702287#0_1', '89702287#0_2']]
lenght_lanes = [[241.41,241.41,241.41],[31.70,31.70],[108.02,108.02,108.02]]
tls = 'tls_7_47'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK7CL49'
ID = 15
edges = ['24323002#1', '89702287#3', '89702288#1']
lanes = [['24323002#1_0', '24323002#1_1'], 
         ['89702287#3_0', '89702287#3_1', '89702287#3_2'],
         ['89702288#1_0', '89702288#1_1', '89702288#1_2']]
lenght_lanes = [[78.98,78.98],[93.80,93.80,93.80],[64.02,64.02,64.02]]
tls = 'tls_7_49'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK7CL53'
ID = 16
edges = ['89700410#0', '-591135051#0', '89702287#7', '42733582#1']
lanes = [['89700410#0_0', '89700410#0_1', '89700410#0_2'], 
         ['-591135051#0_0'],
         ['89702287#7_0', '89702287#7_1', '89702287#7_2'],
         ['42733582#1_0', '42733582#1_1']]
lenght_lanes = [[145.92,145.92,145.92],[92.10],[160.34,160.34,160.34],[66.38,66.38]]
tls = 'tls_7_53'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)

name = 'AK9CL53'
ID = 17
edges = ['38495908#1', '24428867#7', '42733582#0']
lanes = [['38495908#1_0', '38495908#1_1'], 
         ['24428867#7_0', '24428867#7_1'],
         ['42733582#0_0', '42733582#0_1']]
lenght_lanes = [[65.98,65.98],[57.04,57.04],[162.92,162.92]]
tls = 'tls_9_53'
junctions[ID] = junction(name, ID, edges, lanes, lenght_lanes, tls)


#===============================================================


#====================== TLS properties ======================
agent_TLS = {}

tls = 'tls_14_45'
listJunctions = [7]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[
    'GGGGrrrrGGGGrr',
    'rrrrrrrrrrrrrr',
    'rrrrGGGGrrrrGG',
    'YYYYrrrrYYYYrr',
    'uuuurrrruuuurr',    
    'rrrrYYYYrrrrYY',
    'rrrruuuurrrruu' ]
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_14_47'
listJunctions = [8]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[
    'GGGGrrrrGG',
    'rrrrrrrrrr',    
    'rrrrGGGGrr',
    'YYYYrrrrYY',
    'uuuurrrruu',
    'rrrrYYYYrr',
    'rrrruuuurr']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_14_49'
listJunctions = [9]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[
    'GGGGrrGG',
    'rrrrrrrr',    
    'rrrrGGrr',
    'YYYYrrYY',
    'uuuurruu',
    'rrrrYYrr',
    'rrrruurr']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_14_51'
listJunctions = [10]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[
    'rrGGGGGG',
    'rrrrrrrr',    
    'GGrrrrrr',
    'rrYYYYYY',
    'rruuuuuu',
    'YYrrrrrr',
    'uurrrrrr']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_14_53'
listJunctions = [11]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[
    'GGGGrrrrrGGGGrrrr',
    'rrrrrrrrrrrrrrrrr',    
    'rrrrGGGGGrrrrGGGG',
    'YYYYrrrrrYYYYrrrr',
    'uuuurrrrruuuurrrr',
    'rrrrYYYYYrrrrYYYY',
    'rrrruuuuurrrruuuu']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_13_45'
listJunctions = [0]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[
    'GGGGGGGrrrrrr',
    'rrrrrrrrrrrrr',    
    'rrrrrrrGGGGGG',
    'YYYYYYYrrrrrr',
    'uuuuuuurrrrrr',
    'rrrrrrrYYYYYY',
    'rrrrrrruuuuuu']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_13_46_47'
listJunctions = [1,2]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[
    'GGGGrrrGGGGGrrrr',
    'rrrrrrrrrrrrrrrr',    
    'rrrrrrrrrrrrGGGG',
    'YYYYrrrYYYYYrrrr',
    'uuuurrruuuuurrrr',
    'rrrrrrrrrrrrYYYY',
    'rrrrrrrrrrrruuuu']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_13_49_50'
listJunctions = [3, 4]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[
    'GGGGGrrrrGGGGGrrrr',
    'rrrrrrrrrrrrrrrrrr',    
    'rrrrrGGGGrrrrrGGGG',
    'YYYYYrrrrYYYYYrrrr',
    'uuuuurrrruuuuurrrr',
    'rrrrrYYYYrrrrrYYYY',
    'rrrrruuuurrrrruuuu']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_13_51'
listJunctions = [5]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[
    'GGGGrrrr',
    'rrrrrrrr',    
    'rrrrGGGG',
    'YYYYrrrr',
    'uuuurrrr',
    'rrrrYYYY',
    'rrrruuuu']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_13_53'
listJunctions = [6]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[
    'GGGGGrrrrrr',
    'rrrrrrrrrrr',    
    'rrrrrGGGGGG',
    'YYYYYrrrrrr',
    'uuuuurrrrrr',
    'rrrrrYYYYYY',
    'rrrrruuuuuu']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_9_53'
listJunctions = [17]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[
    'rrrrGGGGrr',
    'rrrrrrrrrr',    
    'GGGGrrrrGG',
    'rrrrYYYYrr',
    'rrrruuuurr',
    'YYYYrrrrYY',
    'uuuurrrruu']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_7_45'
listJunctions = [12]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[    
    'GGGGGGGGGGOOrrrrrr',
    'rrrrrrrrrrrrrrrrrr',    
    'rrrrrrrrrrrrGGGGGG',
    'YYYYYYYYYYOOrrrrrr',
    'uuuuuuuuuuOOrrrrrr',
    'rrrrrrrrrrrrYYYYYY',
    'rrrrrrrrrrrruuuuuu']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_7_46'
listJunctions = [13]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[    
    'GGGGGrrrrrrGGG',
    'rrrrrrrrrrrrrr',    
    'rrrrrGGGGGGrrr',
    'YYYYYrrrrrrYYY',
    'uuuuurrrrrruuu',
    'rrrrrYYYYYYrrr',
    'rrrrruuuuuurrr']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_7_47'
listJunctions = [14]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[    
    'GGGGGrrrrrrrGGG',
    'rrrrrrrrrrrrrrr',    
    'rrrrrGGGGGGGrrr',
    'YYYYYrrrrrrrYYY',
    'uuuuurrrrrrruuu',
    'rrrrrYYYYYYYrrr',
    'rrrrruuuuuuurrr']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_7_49'
listJunctions = [15]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[    
    'rrGGGGGGGG',
    'rrrrrrrrrr',    
    'GGrrrrrrrr',
    'rrYYYYYYYY',
    'rruuuuuuuu',
    'YYrrrrrrrr',
    'uurrrrrrrr']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)


tls = 'tls_7_53'
listJunctions = [16]
actionPhases = [0, 1, 2]
auxPhases=[[-1, 3, [3,6]],
           [4, -1, 6],
           [[5,4], 5, -1]]
phases=[    
    'GGGGGrrrGGGGrrrr',
    'rrrrrrrrrrrrrrrr',    
    'rrrrrGGGrrrrGGGG',
    'YYYYYrrrYYYYrrrr',
    'uuuuurrruuuurrrr',
    'rrrrrYYYrrrrYYYY',
    'rrrrruuurrrruuuu']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp)
