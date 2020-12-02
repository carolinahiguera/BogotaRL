'''
Created on 4/09/2016

@author: carolina
'''
import numpy as np
import random
from random import randint
import traci
import struct
import itertools

import var


class edgeAgent():
    def __init__(self, ag_i, ag_j):
        self.SL_i = ag_i
        self.SL_j = ag_j
        self.vertexAgt = [self.SL_i, self.SL_j]
        self.jointActions = list(itertools.product( var.vertexAgents[ag_i].actionPhases, var.vertexAgents[ag_j].actionPhases ))
        self.numActions = len(self.jointActions)
        self.numStates = 0
        self.updatedState = False
        
        #Learning parameters
        self.gamma = 0.95
        self.epsilon = 0.2
        
        #Almacenar discretizacion de estados
        self.dictClusterObjects = {}
        self.numClustersTracker = {}            
        self.mapDiscreteStates = {}
        
        #QValues, QCounts, QAlphas
        self.QValues  = {}
        self.QCounts = {}
        self.QAlphas = {}
        
        self.currStateID = 0
        self.lastStateID = 0
        self.lastJointAction = 0
        
    def initTables(self):
        self.QValues  = np.zeros((self.numStates,self.numActions))
        self.QCounts = np.zeros((self.numStates,self.numActions))
        self.QAlphas = np.ones((self.numStates,self.numActions))
    
    def getJointAction(self):
        ph_i = var.vertexAgents[self.SL_i].currPhaseID
        ph_j = var.vertexAgents[self.SL_j].currPhaseID
        if(ph_i%2 != 0):
            ph_i -= 1
            
        if(ph_j%2 != 0):
            ph_j -= 1
            
        idx = self.jointActions.index((ph_i, ph_j))
        return idx
    
    def updateState(self, currHod):
        state= []        
        for v in self.vertexAgt:
            for edge in var.vertexAgents[v].listEdges:
                state.append(var.vertexAgents[v].queueTracker[edge])    
            for edge in var.vertexAgents[v].listEdges:
                state.append(var.vertexAgents[v].waitingTracker[edge])
        state = np.array(state)
        ki_kj = self.getJointAction()
        stateSubID = int(self.dictClusterObjects[currHod][ki_kj].predict(state))
        self.currStateID = self.mapDiscreteStates[currHod][ki_kj][stateSubID]
    
    def getQValue(self, ai, aj):
        s = self.currStateID
        a = self.jointActions.index((ai, aj))
        return self.QValues[s,a]
    
    def getQVector(self):
        s = self.currStateID
        return self.QValues[s]
    
    def updateQValues(self, bestJointAction):
        s = self.lastStateID
        a = self.lastJointAction
        r_i = var.vertexAgents[self.SL_i].currReward/(1.0*var.vertexAgents[self.SL_i].numNeighbors)
        r_j = var.vertexAgents[self.SL_j].currReward/(1.0*var.vertexAgents[self.SL_j].numNeighbors)
        snew = self.currStateID
        a_i_opt = bestJointAction[self.SL_i]
        a_j_opt = bestJointAction[self.SL_j]
        a_opt = self.jointActions.index((a_i_opt, a_j_opt))
        
        self.QValues[s,a] = self.QValues[s,a] + self.QAlphas[s,a]*(r_i + r_j + (self.gamma*self.QValues[snew,a_opt]) - self.QValues[s,a])
        self.QCounts[s,a] += 1
        self.QAlphas[s,a] = 1/self.QCounts[s,a]
    
    
    def learningPolicy(self, bestJointAction, day, currHod):
        self.updateQValues(bestJointAction)
        seed = (1.0*day)+(currHod/23.0)
        random.seed(seed)
        unigen = random.random()
        #self.epsilon = np.exp(-(1.0/30.0)*((1.0*day)+(currHod/23.0))) 
        self.epsilon = np.exp(-(1.0/60.0)*((1.0*day)+(currHod/23.0))) 

                    
        if(unigen < self.epsilon): #Exploration?
            random.seed()
            action = random.randint(0,len(self.jointActions)-1)
            var.vertexAgents[self.SL_i].newPhaseID = self.jointActions[action][0]
            var.vertexAgents[self.SL_j].newPhaseID = self.jointActions[action][1]
        else:
            ai = bestJointAction[self.SL_i]
            aj = bestJointAction[self.SL_j]
            action = self.jointActions.index((ai, aj))
            var.vertexAgents[self.SL_i].newPhaseID = ai
            var.vertexAgents[self.SL_j].newPhaseID = aj            
        
        self.lastStateID = self.currStateID
        self.lastJointAction = action
    
    def saveLearning(self, day):
        np.savetxt('QValues_edge' + str(self.SL_i) + '_' +  str(self.SL_j) + '_day' + str(day) +'.txt', self.QValues)    
        np.savetxt('QAlphas_edge' + str(self.SL_i) + '_' +  str(self.SL_j) + '_day' + str(day) + '.txt', self.QAlphas)    
        np.savetxt('QCounts_edge' + str(self.SL_i) + '_' +  str(self.SL_j) + '_day' + str(day) + '.txt', self.QCounts)
    
    def loadKnowledge(self, day):
        self.QValues = np.loadtxt('QValues_edge' + str(self.SL_i) + '_' +  str(self.SL_j) + '_day' + str(day) +'.txt' )    
        self.QAlphas = np.loadtxt('QAlphas_edge' + str(self.SL_i) + '_' +  str(self.SL_j) + '_day' + str(day) + '.txt' )    
        self.QCounts = np.loadtxt('QCounts_edge' + str(self.SL_i) + '_' +  str(self.SL_j) + '_day' + str(day) + '.txt' )