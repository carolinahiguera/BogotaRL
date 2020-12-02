'''
Created on Nov 27, 2017

@author: carolina
'''
import var
import numpy as np

class TLS(object):
    '''
    classdocs
    '''


    def __init__(self, ID, listJunctions, phases, actionPhases, auxPhases, beta, theta, exp):
        self.ID = ID
        self.listJunctions = listJunctions
        self.phases = phases
        self.actionPhases = actionPhases
        self.auxPhases = auxPhases
        
         #Almacena informacion del agente por interseccion (colas, tiempo de espera)  
        self.queueEdgeTracker = {}
        self.waitingEdgeTracker = {}
        self.queueLaneTracker = {}
        self.waitingLaneTracker = {}   
        
        #Estado y recompensa     
        self.currReward = 0
        self.currReward2 = 0
        self.currAction = -1
        self.beta = beta
        self.theta = theta 
        self.exp = exp
        
        for j in range(0,len(self.listJunctions)):
            jName = self.listJunctions[j]
            self.queueEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges))
            self.waitingEdgeTracker[j] = np.zeros(len(var.junctions[jName].edges)) #EN MINUTOS
            self.queueLaneTracker[j] = {}
            self.waitingLaneTracker[j] = {}            
            for e in range(0,len(var.junctions[jName].edges)):
                self.queueLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e]))
                self.waitingLaneTracker[j][e] = np.zeros(len(var.junctions[jName].lanes[e])) #EN MINUTOS
     
        
    
    def updateReward1(self):
        reward = 0
        for j in range(0,len(self.listJunctions)):
            jName = self.listJunctions[j]
            for e in range(0,len(var.junctions[jName].edges)):
                a = (self.beta[0]*self.queueEdgeTracker[j][e])**self.theta[0]
                b = (self.beta[1]*self.waitingEdgeTracker[j][e])**self.theta[1]
                reward -= (a + b)
        self.currReward = reward
    
    def updateReward2(self):
        reward = 0
        for j in range(0,len(self.listJunctions)):
            jName = self.listJunctions[j]
            for e in range(0,len(var.junctions[jName].edges)):
                a = (self.queueEdgeTracker[j][e])**self.exp[1]
                b = (self.waitingEdgeTracker[j][e])**self.exp[0]
                reward -= a*b
        self.currReward2 = reward
    
    
        
        