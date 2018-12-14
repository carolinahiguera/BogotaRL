'''
Created on Nov 21, 2017

@author: carolina
'''
import junction
exec(open("./junction.py").read())
import TLS
exec(open("./TLS.py").read())

global port, secondsInDay, episodes, sampleTime
#avilable_ports = [8813, 8814, 8815, 8816, 8817, 8818, 8819, 8820] 
#port = avilable_ports[2]

secondsInDay = 46800#46800
episodes = 200
episodesTest = 5
days2Observe = 5
sampleTime = 10
timeYellow = 2
minTimeGreen = 9#tipico entre 6 y 10seg
maxTimeGreen = minTimeGreen*7
min_numStates = 10
beta = [0.3, 0.7]
pTransfer = 0.2

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
actionPhases = [0,1]
auxPhases = [[-1, [3,2,6]],
             [[5,2,4], -1]]
phases=[
    'GGGGrrrrGGGGrr',
    'rrrrGGGGrrrrGG',
    'rrrrrrrrrrrrrr',    
    'YYYYrrrrYYYYrr',
    'uuuurrrruuuurr',    
    'rrrrYYYYrrrrYY',
    'rrrruuuurrrruu' ]
plan2 = [[63,'GGGGrrrrGGGGrr'],[3,'YYYYrrrrYYYYrr'],[3,'rrrrrrrrrrrrrr'],
         [2,'rrrruuuurrrruu'],[38,'rrrrGGGGrrrrGG'],[3,'rrrrYYYYrrrrYY'],
         [2,'rrrrrrrrrrrrrr'],[3,'uuuurrrruuuurr'],[3,'GGGGrrrrGGGGrr']]
plan3 = [[55,'GGGGrrrrGGGGrr'],[3,'YYYYrrrrYYYYrr'],[3,'rrrrrrrrrrrrrr'],
         [2,'rrrruuuurrrruu'],[49,'rrrrGGGGrrrrGG'],[3,'rrrrYYYYrrrrYY'],
         [2,'rrrrrrrrrrrrrr'],[3,'uuuurrrruuuurr']]
plan4 = [[57,'GGGGrrrrGGGGrr'],[3,'YYYYrrrrYYYYrr'],[4,'rrrrrrrrrrrrrr'],
         [2,'rrrruuuurrrruu'],[44,'rrrrGGGGrrrrGG'],[3,'rrrrYYYYrrrrYY'],
         [1,'rrrrrrrrrrrrrr'],[3,'uuuurrrruuuurr'],[3,'GGGGrrrrGGGGrr']]
#neighbors = ['tls_14_47']
neighbors = ['tls_14_47', 'tls_13_46_47', 'tls_13_45']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)


tls = 'tls_14_47'
listJunctions = [8]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],           
           [[5,2,4], -1]]
phases=[
    'GGGGrrrrGG',        
    'rrrrGGGGrr',
    'rrrrrrrrrr',
    'YYYYrrrrYY',
    'uuuurrrruu',
    'rrrrYYYYrr',
    'rrrruuuurr']
plan2 = [[3,'rrrrrrrrrr'],[2,'uuuurrrruu'],[67,'GGGGrrrrGG'],
         [3,'YYYYrrrrYY'],[2,'rrrrrrrrrr'],[2,'rrrruuuurr'],
         [39,'rrrrGGGGrr'],[2,'rrrrYYYYrr']]
plan3 = [[2,'rrrrYYYYrr'],[2,'rrrrrrrrrr'],[2,'uuuurrrruu'],
         [69,'GGGGrrrrGG'],[3,'YYYYrrrrYY'],[2,'rrrrrrrrrr'],
         [2,'rrrruuuurr'],[37,'rrrrGGGGrr'],[1,'rrrrYYYYrr']]
plan4 = [[75,'GGGGrrrrGG'],[3,'YYYYrrrrYY'],[2,'rrrrrrrrrr'],
         [2,'rrrruuuurr'],[31,'rrrrGGGGrr'],[3,'rrrrYYYYrr'],
         [2,'rrrrrrrrrr'],[2,'uuuurrrruu']]
#neighbors = ['tls_14_45']
neighbors = ['tls_14_45', 'tls_13_46_47', 'tls_14_49']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)


tls = 'tls_14_49'
listJunctions = [9]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[
    'GGGGrrGG',
    'rrrrGGrr',
    'rrrrrrrr',
    'YYYYrrYY',
    'uuuurruu',
    'rrrrYYrr',
    'rrrruurr']
plan2 = [[4,'rrrrGGrr'],[3,'rrrrYYrr'],[2,'rrrrrrrr'],
         [2,'uuuurruu'],[66,'GGGGrrGG'],[3,'YYYYrrYY'],
         [1,'rrrrrrrrrrrrrrrr'],[2,'rrrruurr'],[37,'rrrrGGrr']]
plan3 = [[2,'rrrrGGrr'],[3,'rrrrYYrr'],[2,'rrrrrrrr'],
         [2,'uuuurruu'],[64,'GGGGrrGG'],[3,'YYYYrrYY'],
         [1,'rrrrrrrr'],[2,'rrrruurr'],[41,'rrrrGGrr']]
plan4 = [[68,'GGGGrrGG'],[3,'YYYYrrYY'],[1,'rrrrrrrr'],
         [2,'rrrruurr'],[39,'rrrrGGrr'],[3,'rrrrYYrr'],
         [2,'rrrrrrrr'],[2,'uuuurruu']]
neighbors = ['tls_14_47', 'tls_13_49_50', 'tls_14_51']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)


tls = 'tls_14_51'
listJunctions = [10]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[
    'rrGGGGGG',       
    'GGrrrrrr',
    'rrrrrrrr', 
    'rrYYYYYY',
    'rruuuuuu',
    'YYrrrrrr',
    'uurrrrrr']
plan2 = [[3,'rrrrrrrr'],[2,'rruuuuuu'],[67,'rrGGGGGG'],
         [3,'rrYYYYYY'],[2,'rrrrrrrr'],[2,'uurrrrrr'],
         [39,'GGrrrrrr'],[2,'YYrrrrrr']]
plan3 = [[2,'YYrrrrrr'],[2,'rrrrrrrr'],[2,'rruuuuuu'],
         [69,'rrGGGGGG'],[3,'rrYYYYYY'],[2,'rrrrrrrr'],
         [2,'uurrrrrr'],[37,'GGrrrrrr'],[1,'YYrrrrrr']]
plan4 = [[75,'rrGGGGGG'],[3,'rrYYYYYY'],[2,'rrrrrrrr'],
         [2,'uurrrrrr'],[31,'GGrrrrrr'],[3,'YYrrrrrr'],
         [2,'rrrrrrrr'],[2,'rruuuuuu']]
neighbors = ['tls_14_49', 'tls_13_51', 'tls_14_53']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)

tls = 'tls_14_53'
listJunctions = [11]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[
    'GGGGrrrrrGGGGrrrr',      
    'rrrrGGGGGrrrrGGGG',
    'rrrrrrrrrrrrrrrrr',
    'YYYYrrrrrYYYYrrrr',
    'uuuurrrrruuuurrrr',
    'rrrrYYYYYrrrrYYYY',
    'rrrruuuuurrrruuuu']
plan2 = [[3,'rrrrrrrrrrrrrrrrr'],[2,'uuuurrrrruuuurrrr'],[67,'GGGGrrrrrGGGGrrrr'],
         [3,'YYYYrrrrrYYYYrrrr'],[2,'rrrrrrrrrrrrrrrrr'],[2,'rrrruuuuurrrruuuu'],
         [39,'rrrrGGGGGrrrrGGGG'],[2,'rrrrYYYYYrrrrYYYY']]
plan3 = [[2,'rrrrYYYYYrrrrYYYY'],[2,'rrrrrrrrrrrrrrrrr'],[2,'uuuurrrrruuuurrrr'],
         [69,'GGGGrrrrrGGGGrrrr'],[3,'YYYYrrrrrYYYYrrrr'],[2,'rrrrrrrrrrrrrrrrr'],
         [2,'rrrruuuuurrrruuuu'],[37,'rrrrGGGGGrrrrGGGG'],[1,'rrrrYYYYYrrrrYYYY']]
plan4 = [[75,'GGGGrrrrrGGGGrrrr'],[3,'YYYYrrrrrYYYYrrrr'],[2,'rrrrrrrrrrrrrrrrr'],
         [2,'rrrruuuuurrrruuuu'],[31,'rrrrGGGGGrrrrGGGG'],[3,'rrrrYYYYYrrrrYYYY'],
         [2,'rrrrrrrrrrrrrrrrr'],[2,'uuuurrrrruuuurrrr']]
neighbors = ['tls_14_51', 'tls_13_53']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)

tls = 'tls_13_45'
listJunctions = [0]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[
    'GGGGGGGrrrrrr',        
    'rrrrrrrGGGGGG',
    'rrrrrrrrrrrrr',
    'YYYYYYYrrrrrr',
    'uuuuuuurrrrrr',
    'rrrrrrrYYYYYY',
    'rrrrrrruuuuuu']
plan2 = [[9,'rrrrrrrrrrrrr'],[2,'uuuuuuurrrrrr'],[46,'GGGGGGGrrrrrr'],
         [3,'YYYYYYYrrrrrr'],[2,'rrrrrrrrrrrrr'],[2,'rrrrrrruurrrr'],
         [2,'rrrrrrrGGuuuu'],[37,'rrrrrrrGGGGGG'],[3,'rrrrrrrYYGGGG'],
         [4,'rrrrrrrrrYYYY'],[10,'rrrrrrrrrrrrr']]
plan3 = [[5,'rrrrrrrrrrrrr'],[2,'uuuuuuurrrrrr'],[43,'GGGGGGGrrrrrr'],
         [3,'YYYYYYYrrrrrr'],[2,'rrrrrrrrrrrrr'],[2,'rrrrrrruurrrr'],
         [2,'rrrrrrrGGuuuu'],[40,'rrrrrrrGGGGGG'],[3,'rrrrrrrYYGGGG'],
         [4,'rrrrrrrrrYYYY'],[14,'rrrrrrrrrrrrr']]
plan4 = [[1,'rrrrrrrrrrrrr'],[2,'uuuuuuurrrrrr'],[49,'GGGGGGGrrrrrr'],
         [3,'YYYYYYYrrrrrr'],[2,'rrrrrrrrrrrrr'],[2,'rrrrrrruurrrr'],
         [2,'rrrrrrrGGuuuu'],[34,'rrrrrrrGGGGGG'],[3,'rrrrrrrYYGGGG'],
         [4,'rrrrrrrrrYYYY'],[18,'rrrrrrrrrrrrr']]
neighbors = ['tls_14_45', 'tls_13_46_47', 'tls_7_45']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)

tls = 'tls_13_46_47'
listJunctions = [1,2]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[
    'GGGGrrrGGGGGrrrr',        
    'rrrrrrrrrrrrGGGG',
    'rrrrrrrrrrrrrrrr',
    'YYYYrrrYYYYYrrrr',
    'uuuurrruuuuurrrr',
    'rrrrrrrrrrrrYYYY',
    'rrrrrrrrrrrruuuu']
plan2 = [[15,'rrrrrrrrrrrrGGGG'],[3,'rrrrrrrrrrrrYYYY'],[3,'rrrrrrrrrrrrrrrr'],
         [2,'uuuurrruuuuurrrr'],[48,'GGGGrrrGGGGGrrrr'],[3,'YYYYrrrYYYYYrrrr'],
         [2,'rrrrrrrrrrrruuuu'],[2,'rrrrrrrrrrrrGGGG'],[2,'rrrruuurrrrrGGGG'],
         [27,'rrrrGGGrrrrrGGGG'],[3,'rrrrYYYrrrrrGGGG'],[10,'rrrrrrrrrrrrGGGG']]
plan3 = [[10,'rrrrrrrrrrrrGGGG'],[3,'rrrrrrrrrrrrYYYY'],[3,'rrrrrrrrrrrrrrrr'],
         [2,'uuuurrruuuuurrrr'],[49,'GGGGrrrGGGGGrrrr'],[3,'YYYYrrrYYYYYrrrr'],
         [2,'rrrrrrrrrrrruuuu'],[2,'rrrrrrrrrrrrGGGG'],[2,'rrrruuurrrrrGGGG'],
         [19,'rrrrGGGrrrrrGGGG'],[3,'rrrrYYYrrrrrGGGG'],[22,'rrrrrrrrrrrrGGGG']]
plan4 = [[3,'rrrrrrrrrrrrGGGG'],[3,'rrrrrrrrrrrrYYYY'],[3,'rrrrrrrrrrrrrrrr'],
         [2,'uuuurrruuuuurrrr'],[48,'GGGGrrrGGGGGrrrr'],[3,'YYYYrrrYYYYYrrrr'],
         [2,'rrrrrrrrrrrruuuu'],[2,'rrrrrrrrrrrrGGGG'],[2,'rrrruuurrrrrGGGG'],
         [24,'rrrrGGGrrrrrGGGG'],[3,'rrrrYYYrrrrrGGGG'],[25,'rrrrrrrrrrrrGGGG']]
neighbors = ['tls_13_45', 'tls_14_47', 'tls_13_49_50']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)

tls = 'tls_13_49_50'
listJunctions = [3, 4]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[
    'GGGGGrrrrGGGGGrrrr',        
    'rrrrrGGGGrrrrrGGGG',
    'rrrrrrrrrrrrrrrrrr',
    'YYYYYrrrrYYYYYrrrr',
    'uuuuurrrruuuuurrrr',
    'rrrrrYYYYrrrrrYYYY',
    'rrrrruuuurrrrruuuu']
plan2 = [[18,'rrrrrGGGGrrrrrGGGG'],[3,'rrrrrYYYYrrrrrYYYY'],
         [2,'uuuuurrrruuuuurrrr'],[51,'GGGGGrrrrGGGGGrrrr'],
         [3,'YYYYYrrrrYYYYYrrrr'],[2,'rrrrruuuurrrrruuuu'],
         [41,'rrrrrGGGGrrrrrGGGG']]
plan3 = [[11,'rrrrrGGGGrrrrrGGGG'],[3,'rrrrrYYYYrrrrrYYYY'],
         [2,'uuuuurrrruuuuurrrr'],[51,'GGGGGrrrrGGGGGrrrr'],
         [3,'YYYYYrrrrYYYYYrrrr'],[2,'rrrrruuuurrrrruuuu'],
         [48,'rrrrrGGGGrrrrrGGGG']]
plan4 = [[5,'rrrrrGGGGrrrrrGGGG'],[3,'rrrrrYYYYrrrrrYYYY'],
         [2,'uuuuurrrruuuuurrrr'],[50,'GGGGGrrrrGGGGGrrrr'],
         [3,'YYYYYrrrrYYYYYrrrr'],[2,'rrrrruuuurrrrruuuu'],
         [55,'rrrrrGGGGrrrrrGGGG']]
neighbors = ['tls_13_46_47', 'tls_14_49', 'tls_13_51']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)


tls = 'tls_13_51'
listJunctions = [5]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[
    'GGGGrrrr',        
    'rrrrGGGG',
    'rrrrrrrr',
    'YYYYrrrr',
    'uuuurrrr',
    'rrrrYYYY',
    'rrrruuuu']
plan2 = [[18,'rrrrGGGG'],[3,'rrrrYYYY'],[2,'uuuurrrr'],
         [51,'GGGGrrrr'],[3,'YYYYrrrr'],[2,'rrrruuuu'],
         [41,'rrrrGGGG']]
plan3 = [[11,'rrrrGGGG'],[3,'rrrrYYYY'],[2,'uuuurrrr'],
         [51,'GGGGrrrr'],[3,'YYYYrrrr'],[2,'rrrruuuu'],
         [48,'rrrrGGGG']]
plan4 = [[5,'rrrrGGGG'],[3,'rrrrYYYY'],[2,'uuuurrrr'],
         [50,'GGGGrrrr'],[3,'YYYYrrrr'],[2,'rrrruuuu'],
         [55,'rrrrGGGG']]
neighbors = ['tls_14_51', 'tls_13_49_50', 'tls_13_53']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)

tls = 'tls_13_53'
listJunctions = [6]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], 5, -1]]
phases=[
    'GGGGGrrrrrr',        
    'rrrrrGGGGGG',
    'rrrrrrrrrrr',
    'YYYYYrrrrrr',
    'uuuuurrrrrr',
    'rrrrrYYYYYY',
    'rrrrruuuuuu']
plan2 = [[18,'rrrrrGGGGGG'],[3,'rrrrrYYYYYY'],[2,'uuuuurrrrrr'],
         [51,'GGGGGrrrrrr'],[3,'YYYYYrrrrrr'],[2,'rrrrruuuuuu'],
         [41,'rrrrrGGGGGG']]
plan3 = [[11,'rrrrrGGGGGG'],[3,'rrrrrYYYYYY'],[2,'uuuuurrrrrr'],
         [51,'GGGGGrrrrrr'],[3,'YYYYYrrrrrr'],[2,'rrrrruuuuuu'],
         [48,'rrrrrGGGGGG']]
plan4 = [[5,'rrrrrGGGGGG'],[3,'rrrrrYYYYYY'],[2,'uuuuurrrrrr'],
         [50,'GGGGGrrrrrr'],[3,'YYYYYrrrrrr'],[2,'rrrrruuuuuu'],
         [55,'rrrrrGGGGGG']]
neighbors = ['tls_13_51', 'tls_14_53', 'tls_9_53']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)

tls = 'tls_9_53'
listJunctions = [17]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[
    'rrrrGGGGrr',        
    'GGGGrrrrGG',
    'rrrrrrrrrr',
    'rrrrYYYYrr',
    'rrrruuuurr',
    'YYYYrrrrYY',
    'uuuurrrruu']
plan2 = [[18,'GGGGrrrrGG'],[3,'YYYYrrrrYY'],[2,'rrrruuuurr'],
         [51,'rrrrGGGGrr'],[3,'rrrrYYYYrr'],[2,'uuuurrrruu'],
         [41,'GGGGrrrrGG']]
plan3 = [[11,'GGGGrrrrGG'],[3,'YYYYrrrrYY'],[2,'rrrruuuurr'],
         [51,'rrrrGGGGrr'],[3,'rrrrYYYYrr'],[2,'uuuurrrruu'],
         [48,'GGGGrrrrGG']]
plan4 = [[5,'GGGGrrrrGG'],[3,'YYYYrrrrYY'],[2,'rrrruuuurr'],
         [50,'rrrrGGGGrr'],[3,'rrrrYYYYrr'],[2,'uuuurrrruu'],
         [55,'GGGGrrrrGG']]
neighbors = ['tls_13_53', 'tls_7_53']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)


tls = 'tls_7_45'
listJunctions = [12]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[    
    'GGGGGGGGGGOOrrrrrr',       
    'rrrrrrrrrrrrGGGGGG',
    'rrrrrrrrrrrrrrrrrr', 
    'YYYYYYYYYYOOrrrrrr',
    'uuuuuuuuuuOOrrrrrr',
    'rrrrrrrrrrrrYYYYYY',
    'rrrrrrrrrrrruuuuuu']
plan2 = [[20,'rrrrrrrrrrrrGGGGGG'],[3,'rrrrrrrrrrrrYYYYYY'],
         [2,'rrrrrrrrrrrrrrrrrr'],[2,'uuuuuuuuuuuurrrrrr'],
         [60,'GGGGGGGGGGGGrrrrrr'],[3,'GGGGGYYYYYYYrrrrrr'],
         [10,'GGGGGrrrrrrrrrrrrr'],[3,'YYYYYrrrrrrrrrrrrr'],
         [1,'rrrrrrrrrrrrrrrrrr'],[2,'rrrrrrrrrrrruuuuuu'],
         [14,'rrrrrrrrrrrrGGGGGG']]
plan3 = [[35,'GGGGGGGGGGGGrrrrrr'],[3,'GGGGGYYYYYYYrrrrrr'],
         [10,'GGGGGrrrrrrrrrrrrr'],[3,'YYYYYrrrrrrrrrrrrr'],
         [1,'rrrrrrrrrrrrrrrrrr'],[2,'rrrrrrrrrrrruuuuuu'],
         [37,'rrrrrrrrrrrrGGGGGG'],[3,'rrrrrrrrrrrrYYYYYY'],
         [1,'rrrrrrrrrrrrrrrrrr'],[2,'rrrrrrrrrrrruuuuuu'],
         [37,'rrrrrrrrrrrrGGGGGG'],[3,'rrrrrrrrrrrrYYYYYY'],
         [1,'rrrrrrrrrrrrrrrrrr'],[2,'uuuuuuuuuuuurrrrrr'],
         [23,'GGGGGGGGGGGGrrrrrr']]
plan4 = [[2,'rrrrrrrrrrrrGGGGGG'],[3,'rrrrrrrrrrrrYYYYYY'],
         [1,'rrrrrrrrrrrrrrrrrr'],[2,'uuuuuuuuuuuurrrrrr'],
         [63,'GGGGGGGGGGGGrrrrrr'],[3,'GGGGGYYYYYYYrrrrrr'],
         [10,'GGGGGrrrrrrrrrrrrr'],[3,'YYYYYrrrrrrrrrrrrr'],
         [2,'rrrrrrrrrrrrrrrrrr'],[2,'rrrrrrrrrrrruuuuuu'],
         [29,'rrrrrrrrrrrrGGGGGG']]

neighbors = ['tls_13_45', 'tls_7_46']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)

tls = 'tls_7_46'
listJunctions = [13]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[    
    'GGGGGrrrrrrGGG',        
    'rrrrrGGGGGGrrr',
    'rrrrrrrrrrrrrr',
    'YYYYYrrrrrrYYY',
    'uuuuurrrrrruuu',
    'rrrrrYYYYYYrrr',
    'rrrrruuuuuurrr']
plan2 = [[24,'rrrrrGGGGGGrrr'],[3,'rrrrrYYYYYYrrr'],
         [1,'rrrrrrrrrrrrrr'],[2,'uuuuurrrrrruuu'],
         [71,'GGGGGrrrrrrGGG'],[3,'YYYYYrrrrrrYYY'],
         [2,'rrrrruuuuuurrr'],[14,'rrrrrGGGGGGrrr']]
plan3 = [[53,'GGGGGrrrrrrGGG'],[3,'YYYYYrrrrrrYYY'],
         [2,'rrrrruuuuuurrr'],[33,'rrrrrGGGGGGrrr'],
         [3,'rrrrrYYYYYYrrr'],[1,'rrrrrrrrrrrrrr'],
         [2,'uuuuurrrrrruuu'],[23,'GGGGGrrrrrrGGG']]
plan4 = [[6,'rrrrrGGGGGGrrr'],[3,'rrrrrYYYYYYrrr'],
         [1,'rrrrrrrrrrrrrr'],[2,'uuuuurrrrrruuu'],
         [76,'GGGGGrrrrrrGGG'],[3,'YYYYYrrrrrrYYY'],
         [2,'rrrrruuuuuurrr'],[27,'rrrrrGGGGGGrrr']]
neighbors = ['tls_7_45', 'tls_7_47']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)

tls = 'tls_7_47'
listJunctions = [14]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[    
    'GGGGGrrrrrrrGGG',        
    'rrrrrGGGGGGGrrr',
    'rrrrrrrrrrrrrrr',
    'YYYYYrrrrrrrYYY',
    'uuuuurrrrrrruuu',
    'rrrrrYYYYYYYrrr',
    'rrrrruuuuuuurrr']
plan2 = [[28,'rrrrrGGGGGGGrrr'],[3,'rrrrrYYYYYYYrrr'],
         [2,'uuuuurrrrrrruuu'],[66,'GGGGGrrrrrrrGGG'],
         [3,'YYYYYrrrrrrrYYY'],[2,'rrrrruuuuuuurrr'],
         [16,'rrrrrGGGGGGGrrr']]
plan3 = [[47,'GGGGGrrrrrrrGGG'],[3,'YYYYYrrrrrrrYYY'],
         [2,'rrrrruuuuuuurrr'],[40,'rrrrrGGGGGGGrrr'],
         [3,'rrrrrYYYYYYYrrr'],[2,'uuuuurrrrrrruuu'],
         [23,'GGGGGrrrrrrrGGG']]
plan4 = [[10,'rrrrrGGGGGGGrrr'],[3,'rrrrrYYYYYYYrrr'],
         [2,'uuuuurrrrrrruuu'],[67,'GGGGGrrrrrrrGGG'],
         [3,'YYYYYrrrrrrrYYY'],[2,'rrrrruuuuuuurrr'],
         [33,'rrrrrGGGGGGGrrr']]
neighbors = ['tls_7_46', 'tls_7_49']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)

tls = 'tls_7_49'
listJunctions = [15]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[    
    'rrGGGGGGGG',        
    'GGrrrrrrrr',
    'rrrrrrrrrr',
    'rrYYYYYYYY',
    'rruuuuuuuu',
    'YYrrrrrrrr',
    'uurrrrrrrr']
plan2 = [[3,'YYrrrrrrrr'],[1,'rrrrrrrrrr'],[2,'rruuuuuuuu'],
         [74,'rrGGGGGGGG'],[2,'rrYYYYYYYY'],[2,'uurrrrrrrr'],
         [14,'GGuuuuuuuu']]
plan3 = [[64,'rrGGGGGGGG'],[3,'rrYYYYYYYY'],[2,'uurrrrrrrr'],
         [30,'GGuuuuuuuu'],[3,'YYrrrrrrrr'],[2,'rruuuuuuuu'],
         [16,'rrGGGGGGGG']]
plan4 = [[11,'GGrrrrrrrr'],[3,'YYrrrrrrrr'],[2,'rruuuuuuuu'],[71,'rrGGGGGGGG'],
         [2,'rrYYYYYYYY'],[2,'uurrrrrrrr'],[29,'GGuuuuuuuu']]
neighbors = ['tls_7_47', 'tls_7_53']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)

tls = 'tls_7_53'
listJunctions = [16]
actionPhases = [0, 1]
auxPhases=[[-1, [3,2,6]],
           [[5,2,4], -1]]
phases=[    
    'GGGGGrrrGGGGrrrr',        
    'rrrrrGGGrrrrGGGG',
    'rrrrrrrrrrrrrrrr',
    'YYYYYrrrYYYYrrrr',
    'uuuuurrruuuurrrr',
    'rrrrrYYYrrrrYYYY',
    'rrrrruuurrrruuuu']
plan2 = [[24,'rrrrrGGGrrrrGGGG'],[3,'rrrrrYYYrrrrYYYY'],[1,'rrrrrrrrrrrrrrrr'],
         [2,'uuuuurrruuuurrrr'],[71,'GGGGGrrrGGGGrrrr'],[3,'YYYYYrrrYYYYrrrr'],
         [2,'rrrrruuurrrruuuu'],[14,'rrrrrGGGrrrrGGGG']]
plan3 = [[53,'GGGGGrrrGGGGrrrr'],[3,'YYYYYrrrYYYYrrrr'],[2,'rrrrruuurrrruuuu'],
         [33,'rrrrrGGGrrrrGGGG'],[3,'rrrrrYYYrrrrYYYY'],[1,'rrrrrrrrrrrrrrrr'],
         [2,'uuuuurrruuuurrrr'],[23,'GGGGGrrrGGGGrrrr']]
plan4 = [[6,'rrrrrGGGrrrrGGGG'],[3,'rrrrrYYYrrrrYYYY'],[1,'rrrrrrrrrrrrrrrr'],
         [2,'uuuuurrruuuurrrr'],[76,'GGGGGrrrGGGGrrrr'],[3,'YYYYYrrrYYYYrrrr'],
         [2,'rrrrruuurrrruuuu'],[27,'rrrrrGGGrrrrGGGG']]
neighbors = ['tls_7_49', 'tls_9_53']
agent_TLS[tls] = TLS(tls, listJunctions, phases, actionPhases, auxPhases, beta, 
    neighbors, plan2, plan3, plan4)