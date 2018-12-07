'''
Created on Jan 27, 2018

@author: carolina
'''
import var
import numpy as np
import pandas as pd
import random
import itertools
import gets

class edgeTLS():
    '''
    classdocs
    '''


    def __init__(self, pair_TLS):
        '''
        Constructor
        '''
        self.TLS_i = pair_TLS[0]        
        self.TLS_j = pair_TLS[1]
        self.jointActions = list(itertools.product( var.agent_TLS[self.TLS_i].actionPhases, var.agent_TLS[self.TLS_j].actionPhases ))
        self.numJointActions = len(self.jointActions)
        self.numJointStates = 0
        
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
        
        #joint state and action
        self.currJointState = -1
        self.currJointAction = -1
        self.lastJointState = -1
        self.lastJointAction = -1
        
    def initialize(self):
        self.QValues  = np.zeros((self.numJointStates,self.numJointActions))
        self.QCounts = np.zeros((self.numJointStates,self.numJointActions))
        self.QAlphas = np.ones((self.numJointStates,self.numJointActions))
    
    def getJointAction(self):
        act_i = var.agent_TLS[self.TLS_i].currAction    
        act_j = var.agent_TLS[self.TLS_j].currAction         
        self.currJointAction = self.jointActions.index( (act_i, act_j) )
        
    def getJointState(self):
        state = gets.getObservation_NB(self.TLS_i, self.TLS_j)
        state = np.array(state)
        stateID = int(self.dictClusterObjects.predict(state.reshape(1,-1)))
        self.currJointState = self.mapDiscreteStates[stateID]
    
    def updateStateAction(self):
        self.lastJointAction = self.currJointAction
        self.lastJointState = self.currJointState
    
    def getQValue(self, ai, aj):
        s_ij = self.currJointState
        a_ij = self.jointActions.index( (ai, aj) )
        return self.QValues[s_ij, a_ij]
    
    def learnPolicy(self, act_VE):        
        s = self.lastJointState
        a = self.lastJointAction
        s_ = self.currJointState
        jAct = ( act_VE[self.TLS_i], act_VE[self.TLS_j] )
        a_ = self.jointActions.index( jAct )
        r = var.agent_TLS[self.TLS_i].currReward + var.agent_TLS[self.TLS_j].currReward 
        alpha = self.QAlphas[s,a]
        lastQ = self.QValues[s,a]
        maxQ = self.QValues[s_, a_]
        self.QValues[s,a] = lastQ + alpha*(r + self.gamma*maxQ - lastQ)
        self.QCounts[s,a] += 1.0
        self.QAlphas[s,a] = 1.0/self.QCounts[s,a]
    
    def saveLearning(self, day):
        df = pd.DataFrame(self.QValues); df.to_csv('./csv_files_learning/QValues_tls' + str(self.TLS_i) + '_nb' +  str(self.TLS_j) + '_day' + str(day) + '.csv')
        df = pd.DataFrame(self.QAlphas); df.to_csv('./csv_files_learning/QAlphas_tls' + str(self.TLS_i) + '_nb' +  str(self.TLS_j) + '_day' + str(day) + '.csv')
        df = pd.DataFrame(self.QCounts); df.to_csv('./csv_files_learning/QCounts_tls' + str(self.TLS_i) + '_nb' +  str(self.TLS_j) + '_day' + str(day) + '.csv')
    
   
        
        